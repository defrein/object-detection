from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import render_boxes


export ROBOFLOW_API_KEY="Iq3ivV7a6xQZ190yZfLe"

pipeline = InferencePipeline.init(
    model_id="model_id/version",
    video_reference="video.mp4", # Replace with the path to your video
    on_prediction=render_boxes, # Function to run after each prediction
)
pipeline.start()
pipeline.join()