from transformers import AutoFeatureExtractor, AutoModelForImageClassification

class LIMInvoker:
    def lim_invoker(self, image):
        try:
            feature_extractor = AutoFeatureExtractor.from_pretrained("google/vit-base-patch16-224")
            model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")
            inputs = feature_extractor(images=image, return_tensors="pt")
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            
            # Get the predicted label
            predicted_label = model.config.id2label[predicted_class_idx]
            
            # Add image recognition result to chat
            image_response = f"I see an image of {predicted_label}."
            return image_response
        except:
            return "I'am sorry but the image couldn't be processed!"
