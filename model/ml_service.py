import time
import redis
import os
import settings
import tensorflow
import numpy as np
import json
from tensorflow.keras.applications import resnet50
from tensorflow.keras.preprocessing import image



# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
    host = settings.REDIS_IP,
    port = settings.REDIS_PORT,
    db = settings.REDIS_DB_ID
    )

# TODO
# Load your ML model and assign to variable `model`
model = resnet50.ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    # TODO

    ima = image.load_img(os.path.join(settings.UPLOAD_FOLDER, image_name), target_size=(224, 224))

    img_array = image.img_to_array(ima)

    img_array = np.expand_dims(img_array, axis=0)

    img_array = resnet50.preprocess_input(img_array)

    preds = model.predict(img_array)

    preds = resnet50.decode_predictions(preds, top=1)

    class_name = preds[0][0][1]
    pred_probability = preds[0][0][2]

    pred_probability = round(float(pred_probability),4)

    return tuple([class_name, pred_probability])


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO

        queue, job_qd = db.brpop(settings.REDIS_QUEUE)
        job_qd  = json.loads(job_qd)

        pred_class, pred_score = predict(job_qd["image_name"])
        output = { 
            "prediction": pred_class,
            "score": pred_score,
              }

        db.set(job_qd["id"], json.dumps(output))


        # Don't forget to sleep for a bit at the end
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()