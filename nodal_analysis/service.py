import logging
from collections import Counter

from common.handlers.base import MessageHandler
from common.models.point import Point
from gateway_service.manager import GatewayManager
from gateway_service.models import TaskStatus
from gateway_service.schemas import TaskSchema

from nodal_analysis.schemas import NodeAnalysisRequest
from nodal_analysis.settings import ServiceSettings


class NodalAnalysisService(MessageHandler):
    def __init__(self):
        super().__init__()
        self.settings = ServiceSettings()
        self.gateway_service_manager = GatewayManager(self.settings.gateway_service_url)

    async def _process_message(self, request: NodeAnalysisRequest):
        logging.info(f"request received, task {request.id}")
        intersection_points: list[Point] = []
        vlp_points = self._convert_vlp_data_to_point(request)
        ipr_points = self._convert_ipr_data_to_point(request)
        all_points = vlp_points + ipr_points
        # исходим из того, что каждая точка в vlp и ipr имеет уникальные координаты
        # (в рамках своего массива)
        point_counter = Counter(all_points)

        for point, quantity in point_counter.items():
            if quantity > 1:
                intersection_points.append(point)

        updated_task = TaskSchema(
            id=request.id, status=TaskStatus.processed, nodal_analysis=intersection_points
        )
        await self.gateway_service_manager.update_task(task_schema=updated_task)
        logging.info(f"task {request.id} processed")

    def _convert_vlp_data_to_point(self, request: NodeAnalysisRequest) -> list[Point]:
        points = []
        for count, q_liq in enumerate(request.vlp.q_liq):
            point = Point(q_liq=q_liq, p_wf=request.vlp.p_wf[count])
            points.append(point)
        return points

    def _convert_ipr_data_to_point(self, request: NodeAnalysisRequest) -> list[Point]:
        points = []
        for count, q_liq in enumerate(request.ipr.q_liq):
            point = Point(q_liq=q_liq, p_wf=request.ipr.p_wf[count])
            points.append(point)
        return points
