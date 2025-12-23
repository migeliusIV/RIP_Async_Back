# quantum/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import time
from concurrent import futures

# --- НАСТРОЙКИ ---
GO_SERVICE_URL = "http://127.0.0.1:8080/internal/quantum_tasks/updating"
AUTH_TOKEN = "secret12"

# Пул потоков (fire-and-forget)
executor = futures.ThreadPoolExecutor(max_workers=1)


def update_task_logic(task_id: int):
    """
    Асинхронная логика:
    формирует новое описание задачи и отправляет PUT в Go
    """
    print(f"[QuantumWorker] Start processing task_id={task_id}")

    try:
        # имитация задержки (если нужно — можно убрать)
        time.sleep(5)

        # Формируем payload
        payload = {
            "id_task": task_id,
            "task_description": "Заявка выполнена"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{AUTH_TOKEN}",
        }

        print(f"[QuantumWorker] Sending PUT to Go for task_id={task_id}")
        resp = requests.put(
            GO_SERVICE_URL,
            json=payload,
            headers=headers,
            timeout=5
        )

        print(f"[QuantumWorker] Go response: {resp.status_code}")

    except Exception as e:
        print(f"[QuantumWorker] Error for task_id={task_id}: {e}")


@api_view(["POST"])
def perform_calculation(request):
    """
    POST:
    принимает { id_task }
    запускает фоновую задачу
    сразу отвечает 200 OK
    """
    try:
        task_id = request.data.get("id_task")

        if not task_id:
            return Response(
                {"error": "id_task is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fire-and-forget
        executor.submit(update_task_logic, int(task_id))

        return Response(
            {"message": "Task processing started", "id_task": task_id},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
