from app.core.containers.main_container import MainContainer
from app.core.orchestrators.main_orchestrator import MainOrchestrator


container = MainContainer()

app = MainOrchestrator(
    container
)


result = app.run(
    "AI-Studio projesinin dosya yapısını analiz et"
)


print("\n===== RESULT =====")
print(result)
print("==================")