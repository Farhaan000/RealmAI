from transformers import AutoFeatureExtractor, AutoModelForImageClassification

class LIMInvoker:
    def lim_invoker(self, image):
        try:
            # Load the feature extractor and model
            feature_extractor = AutoFeatureExtractor.from_pretrained(
                "google/vit-base-patch16-224",
                do_rescale=False  # Disable rescaling
            )
            model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")
            
            print("image.max()", image.max())
            # Ensure the image tensor is correctly scaled between 0 and 1
            if image.max() > 1.0:
                image = image / 255.0  # Normalize image to [0, 1] range

            # Check if the image tensor has the correct shape
            print(f"Image tensor shape: {image.shape}")

            # Process the image with the feature extractor
            inputs = feature_extractor(images=image, return_tensors="pt")
            # print(f"Feature extractor inputs: {inputs}")

            # Get model outputs
            outputs = model(**inputs)
            logits = outputs.logits
            # print(f"Logits: {logits}")

            # Get the predicted class index
            predicted_class_idx = logits.argmax(-1).item()
            print(f"Predicted class index: {predicted_class_idx}")

            # Get the predicted label
            predicted_label = model.config.id2label[predicted_class_idx]
            print(f"Predicted label: {predicted_label}")

            # Add image recognition result to chat
            image_response = f"I see an image of {predicted_label}."
            return image_response
        except Exception as e:
            print(f"Error: {e}")
            return "I'm sorry, but the image couldn't be processed!"
