from rest_framework.views import APIView
from rest_framework.response import Response
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

MODEL_DIR = "model"
model, tokenizer = None, None

def load_model_and_tokenizer():
    global model, tokenizer
    if model is None or tokenizer is None:
        model = BertForSequenceClassification.from_pretrained(MODEL_DIR)
        tokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
        model.eval()
    return model, tokenizer

class DiagnoseCarIssue(APIView):
    def post(self, request, *args, **kwargs):
        model, tokenizer = load_model_and_tokenizer()

        symptoms = request.data.get("symptoms", "")
        if not symptoms:
            return Response({"error": "No symptoms provided"}, status=400)

        inputs = tokenizer(
            symptoms,
            return_tensors="pt",
            max_length=512,
            padding="max_length",
            truncation=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
        predictions = torch.sigmoid(outputs.logits).squeeze().numpy()
        causes_class_ids = [i for i, pred in enumerate(predictions) if pred > 0.5]
        causes = self.get_causes_from_class_ids(causes_class_ids)
        
        response = self.generate_response(symptoms, causes)
        return Response({"response": response}, status=200)

    def get_causes_from_class_ids(self, class_ids):
        cause_mapping = {
            0: "износ подшипников",
            1: "низкий уровень масла",
            2: "износ тормозных дисков",
            3: "поврежденный глушитель",
            4: "износ тормозных колодок",
            5: "коррозия тормозных дисков",
            6: "дисбаланс колес",
            7: "поврежденная рулевая рейка",
            8: "забитый топливный фильтр",
            9: "неисправный турбокомпрессор",
            10: "недостаток охлаждающей жидкости",
            11: "неисправность термостата",
            12: "неисправность каталитического нейтрализатора",
            13: "неисправность системы EGR",
            14: "засорение дроссельной заслонки",
            15: "неисправность форсунок",
            16: "износ ступичных подшипников",
            17: "поврежденный шрусовой привод",
            18: "неисправность сцепления",
            19: "износ синхронизаторов коробки передач",
            20: "неисправность подвески",
            21: "износ амортизаторов",
            22: "неисправность масляного уплотнителя",
            23: "повреждение прокладки поддона",
            24: "износ подшипников колес",
            25: "дисбаланс шин",
            26: "утечка тормозной жидкости",
            27: "неисправность вентилятора радиатора",
            28: "неисправность генератора",
            29: "неисправность проводки",
            30: "протечка охлаждающей жидкости",
            31: "неисправность датчика массового расхода воздуха",
            32: "неисправность турбины",
            33: "неисправность лямбда-зонда",
            34: "забитый воздушный фильтр",
            35: "износ сайлентблоков",
            36: "недостаток масла в коробке передач",
            37: "неисправность стартера",
            38: "неисправность аккумулятора",
            39: "износ шаровых опор",
            40: "повреждение стабилизатора",
            41: "неисправность датчика положения дроссельной заслонки",
            42: "износ маховика",
            43: "деформация тормозных дисков",
            44: "забитый каталитический нейтрализатор",
            45: "износ рулевого вала",
            46: "неисправность рулевой тяги",
            47: "неисправность датчика кислорода",
            48: "неисправность системы зажигания",
            49: "неисправность топливного насоса"
        }
        return [cause_mapping.get(class_id, "Неизвестная причина") for class_id in class_ids]

    def generate_response(self, symptoms, causes):
        response_template = (
            f"Здравствуйте! Вы описали следующие симптомы: '{symptoms}'. "
            f"Это может быть вызвано следующими причинами: '{', '.join(causes)}'. "
            f"Вы можете забронировать место в живой очереди в нашем автосервисе или записаться на удобную для вас дату и время. "
            f"Если у вас есть еще вопросы, пожалуйста, обратитесь в поддержку к Администратору для дополнительной информации."
        )
        return response_template