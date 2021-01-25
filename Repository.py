import sqlite3
import DaoGen
import Dtos


# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('database.db')
        self.logistics = DaoGen.Dao(Dtos.Logistic, self._conn)
        self.clinics = DaoGen.Dao(Dtos.Clinic, self._conn)
        self.suppliers = DaoGen.Dao(Dtos.Supplier, self._conn)
        self.vaccines = DaoGen.Dao(Dtos.Vaccine, self._conn)

    def close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE logistics (
            id             INTEGER     PRIMARY KEY,
            name           STRING      NOT NULL,
            count_sent     INTEGER     NOT NULL,
            count_received INTEGER     NOT NULL 
        );
        CREATE TABLE clinics (
            id             INTEGER     PRIMARY KEY,
            location       STRING      NOT NULL,
            demand         INTEGER     NOT NULL,
            logistic       INTEGER     REFERENCES logistics(id)
        );
        CREATE TABLE suppliers (
            id             INTEGER     PRIMARY KEY,
            name           STRING      NOT NULL,
            logistic       INTEGER     REFERENCES logistics(id)
        );
          CREATE TABLE vaccines (
            id             INTEGER     PRIMARY KEY,
            date           DATE        NOT NULL,
            supplier       INTEGER     REFERENCES suppliers(id),
            quantity       INTEGER     NOT NULL
        );
        """)

    def get_output_line(self):
        curs = self._conn.cursor()
        curs.execute('SELECT SUM(quantity) FROM vaccines')
        output_line_as_list = list(curs.fetchone())
        curs.execute('SELECT SUM(demand) FROM clinics')
        output_line_as_list = output_line_as_list + list(curs.fetchone())
        curs.execute('SELECT SUM(count_received) FROM logistics')
        output_line_as_list = output_line_as_list + list(curs.fetchone())
        curs.execute('SELECT SUM(count_sent) FROM logistics')
        output_line_as_list = output_line_as_list + list(curs.fetchone())
        output_line = ''
        for out in output_line_as_list:
            output_line += str(out) + ','
        return output_line[:-1]

    def send_shipment(self, location, amount_of_vaccines_to_send):
        curs = self._conn.cursor()
        curs.execute('SELECT id,demand,logistic FROM clinics WHERE location="{}"'.format(location))
        clinic_instance = curs.fetchone()  # get the clinic of the location in the order
        self.clinics.update({'demand': '{}'.format(int(clinic_instance[1]) - int(amount_of_vaccines_to_send))},
                            {'id': int(clinic_instance[0])})  # update demand in clinic record in clinics table

        # gets table ordered by date of: vac.id | vac.quantity | vac.sup.id | vac.sup.log.id
        curs.execute("""SELECT vac.id, vac.quantity, sup.id, sup.logistic
                        FROM vaccines as vac JOIN suppliers as sup JOIN logistics as log 
                        ON vac.supplier=sup.id AND sup.logistic=log.id ORDER BY vac.date""")
        shipment_data_info_list = curs.fetchall()  # all the data from the asked table as list of tuples

        amount_of_vaccines_left = int(amount_of_vaccines_to_send)  # amount that left to deliver

        for curr_vax_pack in shipment_data_info_list:  # iterating on each tuple with the necessary data
            if not amount_of_vaccines_left > 0:  # if there are no more vaccines to deliver
                break
            # get updated relevant count_sent
            logistic_instance_count_sent = curs.execute(
                'SELECT count_sent FROM logistics WHERE id={}'.format(clinic_instance[2])).fetchone()

            quantity_demand_gap = int(curr_vax_pack[1]) - amount_of_vaccines_left

            if quantity_demand_gap >= 0:  # at least enough quantity of vaccines than demanded
                self.vaccines.update({'quantity': '{}'.format(quantity_demand_gap)},
                                     {'id': '{}'.format(curr_vax_pack[0])})  # update vaccine record in vaccine table
                self.logistics.update(
                    {'count_sent': '{}'.format(logistic_instance_count_sent[0] + amount_of_vaccines_left)},
                    {'id': '{}'.format(clinic_instance[2])})  # update logistic record in logistic table
                amount_of_vaccines_left = 0  # delivered all required amount of vaccines

            else:  # quantity_demand_gap < 0 - means that we need another entry of vaccine table
                self.vaccines.update({'quantity': '0'}, {
                    'id': '{}'.format(curr_vax_pack[0])})  # update vaccine record quantity in vaccine table to 0
                self.logistics.update({'count_sent': '{}'.format(logistic_instance_count_sent[0] + curr_vax_pack[1])},
                                      {'id': '{}'.format(
                                          clinic_instance[2])})  # update logistic record in logistic table
                amount_of_vaccines_left = -quantity_demand_gap

        self.vaccines.delete(**{'quantity': 0})  # remove all the empty quantity vaccines records

        print("send")  # finish with repo_commit

    def received_shipment(self, supplier_name, amount_of_vaccines, date):
        curs = self._conn.cursor()

        curs.execute('SELECT id,logistic FROM suppliers WHERE {}="{}"'.format('name', supplier_name))
        supplier_instance = curs.fetchone()  # get the supplier from db
        self.vaccines.insert(Dtos.Vaccine(date, supplier_instance[0], amount_of_vaccines))

        curs.execute('SELECT count_received FROM logistics WHERE id="{}"'.format(supplier_instance[1]))
        logistic_instance = curs.fetchone()  # get the logistic of the previous supplier from db
        self.logistics.update({'count_received': '{}'.format(int(amount_of_vaccines) + logistic_instance[0])},
                              {'id': int(supplier_instance[1])})
        print("received")

    def print_db(self):
        self._print_vaccines()
        self._print_suppliers()
        self._print_clinics()
        self._print_logistics()

    def _print_vaccines(self):
        curs = self._conn.cursor()
        curs.execute("SELECT * FROM vaccines")
        lst = curs.fetchall()
        print("Vaccines:")
        for rec in lst:
            print(rec)

    def _print_suppliers(self):
        curs = self._conn.cursor()
        curs.execute("SELECT * FROM suppliers")
        lst = curs.fetchall()
        print("Suppliers:")
        for rec in lst:
            print(rec)

    def _print_clinics(self):
        curs = self._conn.cursor()
        curs.execute("SELECT * FROM clinics")
        lst = curs.fetchall()
        print("Clinics:")
        for rec in lst:
            print(rec)

    def _print_logistics(self):
        curs = self._conn.cursor()
        curs.execute("SELECT * FROM logistics")
        lst = curs.fetchall()
        print("Logistics:")
        for rec in lst:
            print(rec)


repo = _Repository()
repo.create_tables()
