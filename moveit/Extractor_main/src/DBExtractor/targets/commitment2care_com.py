"""
doc
"""
import datetime
import os
from collections import namedtuple

from .targets_base import ExtractorBase
from ..gpg.commitment2care_com import Commitment2care as Gpg
from ..sql.commitment2care_com import Commitment2care as Db
from ..ftp.commitment2care_com import Commitment2care as Ftp


class Commitment2care(ExtractorBase):
    """
    Class
    """

    def __init__(self, args, config):
        super().__init__(args, config)
        self.__db = Db(args, config)
        self.__gpg = Gpg(args, config)
        self.__ftp = Ftp(args, config)
        self.start_date = (datetime.date.today() -
                           datetime.timedelta(days=int(self.config.get(self.args.domain, "interval"))))
        self.end_date = datetime.date.today()

    def execute(self):
        """

        :param config:
        :return:
        """

        file_name_prefix = self.config.get(self.args.domain, "file_name_prefix")
        file_name_date_format = self.config.get(self.args.domain, "file_name_date_format")

        try:
            data_table = self._get_sql_data()
        finally:
            self.__db.disconnect()

        file_date = self.end_date.strftime(file_name_date_format)
        data_directory_path = self.config.get(self.args.domain, "data_directory_path")
        domain_data_directory_path = f'{data_directory_path}/{self.args.domain}'

        if not os.path.exists(domain_data_directory_path):
            os.makedirs(domain_data_directory_path)

        file_name_to_write = f"{domain_data_directory_path}/{file_name_prefix}{file_date}.csv"

        if os.path.exists(file_name_to_write):
            os.remove(file_name_to_write)
        if os.path.exists(f'{file_name_to_write}.gpg'):
            os.remove(f'{file_name_to_write}.gpg')
        self._write_to_csv(file_name_to_write, data_table)

        if os.path.exists(file_name_to_write):
            self.__gpg.encrypt(file_name_to_write)
            if os.path.exists(f"{file_name_to_write}.gpg"):
                ftp_target_dir = self.config.get(self.args.domain, f'{self.args.env}_ftp_target_dir')
                self.__ftp.upload_file(f"{file_name_to_write}.gpg",
                                       f"{ftp_target_dir}/{file_name_prefix}{file_date}.csv.gpg")
            else:
                self.logger.error(f"File {file_name_to_write}.gpg not found")
        else:
            self.logger.error(f"File {file_name_to_write} not found")

    def _get_sql_data(self):
        """
        Get data from sql
        :return:
        """

        result_table = [['FirstName', 'LastName', 'EmailAddress', 'PracticeOffice',
                         'OfficeZipCode', 'CreationDate', 'AbbVieRep', 'HCPPharmacist', 'Branded']]
        data = dict(self.__db.select_ref_data_office_and_practice())
        practice_office_id = data['Your Practice/Office']
        abbvie_sales_rep_id = data['AbbVie Sales Representative']

        data = dict(self.__db.select_ref_data_pharm_and_health_care())
        pharm_id = data["I'm a Pharmacist"]
        health_care_id = data["I'm a Health Care Provider"]

        start_date = self.start_date.strftime("%Y-%m-%d")
        end_date = self.end_date.strftime("%Y-%m-%d")
        creation_date_format = self.config.get(self.args.domain, "creation_date_format")

        user_response_data = self.__db.select_user_response_data(start_date, end_date)
        Result = namedtuple('Result',
                            ['id', 'StartDate', 'TextAnswer', 'OptionId',
                             'Name', 'FirstName', 'LastName', 'Email', 'ZipCode'])
        result_list = [Result(*row) for row in user_response_data]

        result_dict = {}
        for result in result_list:
            if result.id in result_dict:
                result_dict[result.id].append(result)
            else:
                result_dict[result.id] = [result]
        first_name = None
        last_name = None
        email = None
        practice_office = None
        zip_code = None
        creation_date = None
        abbvie_rep = None
        hcp_pharmacist = None
        branded = None

        for key, value in result_dict.items():
            flag = True
            first_name = ""
            last_name = ""
            email = ""
            practice_office = ""
            zip_code = ""
            creation_date = ""
            abbvie_rep = ""
            hcp_pharmacist = ""
            branded = ""
            for item in value:
                if flag:
                    first_name = item.FirstName
                    last_name = item.LastName
                    email = item.Email
                    zip_code = item.ZipCode
                    creation_date = item.StartDate.strftime(creation_date_format)
                    flag = False
                if item.OptionId == abbvie_sales_rep_id:
                    abbvie_rep = item.TextAnswer
                elif item.OptionId == pharm_id:
                    hcp_pharmacist = "I'm a Pharmacist"
                elif item.OptionId == health_care_id:
                    hcp_pharmacist = "I'm a Health Care Provider"
                elif item.OptionId == practice_office_id:
                    practice_office = item.TextAnswer
                else:
                    if item.Name == "C2C Quiz Unbranded":
                        branded = "Unbranded"
                    elif item.Name == "C2C Quiz Branded HCP":
                        branded = "Branded"
                    elif item.Name == "C2C Quiz Branded Pharmacist":
                        branded = "Branded"

            result_table.append([first_name, last_name, email, practice_office, zip_code, creation_date,
                                 abbvie_rep, hcp_pharmacist, branded])
        return result_table

    def _write_to_csv(self, file_name, data_table):
        with open(file_name, 'w') as f:
            for row in data_table:
                f.write(','.join(row) + '\n')

    def _get_file_to_encrypt(self, directory):
        return sorted(os.listdir(directory), reverse=True)
