class ProductModel:
    def __init__(self, key, category, product, caption, image, created_by=None):
        self.key = key
        self.category = category
        self.product = product
        self.caption = caption
        self.image = image if isinstance(image, list) else [image]
        self.created_by = created_by

