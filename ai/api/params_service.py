
from ai.models.post_params_config import ParamsFieldModel, ParamsFieldValueModel


def get_params_value(params, key) -> ParamsFieldValueModel():
    return ParamsService().get_params_value_model(params, key)


class ParamsService:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            # Your initialization code here
            cls.__instance.cache = {}
        return cls.__instance

    def get_params_value_model(self, params, key) -> ParamsFieldValueModel:
        value = params[key]
        model = ParamsFieldValueModel.objects.filter(
            param_field__params_code=key, post_value=value).first()

        if model is None:
            f = ParamsFieldModel.objects.filter(params_code=key).first()
            f.default_value

        return model
