class RequestQuote:
    def __init__(self, company_name, full_name, email,address, tel, job, origin_destination, product_name,
weight_dimensions,service,  container_size,created_by=None):
        self.company_name = company_name
        self.full_name = full_name
        self.email = email
        self.address = address
        self.tel = tel
        self.job = job
        self.origin_destination = origin_destination
        self.product_name = product_name
        self.weight_dimensions = weight_dimensions
        self.service = service
        self.container_size = container_size
        self.created_by = created_by