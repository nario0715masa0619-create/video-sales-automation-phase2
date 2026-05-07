from vsa.config.settings import Settings

def test_settings_defaults():
    settings = Settings(env="development")
    assert settings.env == "development"
    assert settings.debug is False
