# DTOs of DB

class Vaccine:
    vaccine_record_counter = 0

    def __init__(self, date, supplier, quantity):
        self.id = Vaccine.vaccine_record_counter
        self.date = date
        self.supplier = int(supplier)
        self.quantity = int(quantity)
        Vaccine.vaccine_record_counter += 1


class Logistic:
    def __init__(self, id, name, count_sent, count_received):
        self.id = int(id)
        self.name = str(name)
        self.count_sent = int(count_sent)
        self.count_received = int(count_received)


class Clinic:
    def __init__(self, id, location, demand, logistic):
        self.id = int(id)
        self.location = str(location)
        self.demand = int(demand)
        self.logistic = int(logistic)


class Supplier:
    def __init__(self, id, name, logistic):
        self.id = int(id)
        self.name = str(name)
        self.logistic = int(logistic)
