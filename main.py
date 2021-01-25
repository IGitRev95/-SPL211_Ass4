import sys
import Dtos
from Repository import repo


def main(args):
    config_pars_n_set(args[1])
    with open(args[3], "w") as output_file:
        orders_file = open(args[2])
        orders_list = orders_file.read().splitlines()
        orders_file.close()
        order_index = 0
        for order in orders_list:
            order = order.split(',')
            if len(order) == 2:
                repo.send_shipment(*order)
            else:
                repo.received_shipment(*order)
            output_file.write(repo.get_output_line())
            if order_index < len(orders_list)-1:
                output_file.write('\n')
            order_index += 1
    repo.close()
    print("finish")


def config_pars_n_set(input_file_path):
    input_config_file = open(input_file_path)
    data = input_config_file.read().splitlines()
    input_config_file.close()
    data_quantity = data[0].split(',')
    vaccine_start_index = 1
    supplier_start_index = vaccine_start_index+int(data_quantity[0])
    clinic_start_index = supplier_start_index+int(data_quantity[1])
    logistic_start_index = clinic_start_index+int(data_quantity[2])

    for i in range(logistic_start_index, len(data)):
        repo.logistics.insert(Dtos.Logistic(*data[i].split(',')))

    for i in range(clinic_start_index, logistic_start_index):
        repo.clinics.insert(Dtos.Clinic(*data[i].split(',')))

    for i in range(supplier_start_index, clinic_start_index):
        repo.suppliers.insert(Dtos.Supplier(*data[i].split(',')))

    for i in range(vaccine_start_index, supplier_start_index):
        repo.vaccines.insert(Dtos.Vaccine(*data[i].split(',')[1:]))  # cutting given id cause getting from app


if __name__ == '__main__':
    main(sys.argv)
