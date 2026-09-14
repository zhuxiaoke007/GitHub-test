from contact_manager.id_generator import UuidContactIdGenerator


def test_generate_returns_nonempty_string():
    generator = UuidContactIdGenerator()

    contact_id = generator.generate()

    assert isinstance(contact_id, str)
    assert contact_id != ""


def test_generate_returns_unique_ids():
    generator = UuidContactIdGenerator()

    first = generator.generate()
    second = generator.generate()

    assert first != second
