#id_generator.py
import uuid
from contact_manager.protocols import ContactIdGenerationError

# ============ 实现 ============
class UuidContactIdGenerator:
    """基于 UUID4 的 ID 生成器。"""
    def generate(self) -> str:
        try:
            return str(uuid.uuid4())
        except Exception as e:
            raise ContactIdGenerationError("无法生成联系人 ID") from e