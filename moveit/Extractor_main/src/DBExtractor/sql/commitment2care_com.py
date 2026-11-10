import inspect
import os

import pyodbc

from .sql_base import SqlBase


class Commitment2care(SqlBase):
    """
    Class
    """

    def __init__(self, args, config):
        """
        Constructor
        :param config:
        """
        super().__init__(args, config)
        self.__database_name = config.get(args.domain, "database_name")
        self.__database_type = config.get(args.domain, "database_type")
        self.__driver_name = config.get(self.__database_type, "driver_name")

    def connect(self):
        """
        Connect to the database engine
        :return:
        """
        pword = self.password_fixup(os.getenv("RDS_PASSWD"))

        self.connection = pyodbc.connect(driver="{" + self.__driver_name + "}",
                                         server=os.getenv("RDS_ENDPOINT"),
                                         database=self.__database_name,
                                         uid=os.getenv("RDS_USER"),
                                         pwd=pword,
                                         readonly=True)

    def select_ref_data_office_and_practice(self):
        """
        Select reference data for office and practice
        :return:
        """
        query = "SELECT Question.Text, QuestionOption.Id FROM Question " + \
                "INNER JOIN QuestionOption ON Question.Id = QuestionOption.QuestionId " + \
                "WHERE QuestionOption.Text != 'options' " + \
                "AND Question.Text IN ('Your Practice/Office', 'AbbVie Sales Representative')"

        return self.execute_query_fetchall(query, inspect.currentframe().f_code.co_name)

    def password_fixup(self, pword):
        """
        Fixup password
        :return:
        """
        fixed_pword = ""
        special_char_found = False
        for ch in pword:
            if ch in "[!@*(){}|:?],=&":
                special_char_found = True
                if ch == "}":
                    fixed_pword += ch + ch
                else:
                    fixed_pword += ch
            else:
                fixed_pword += ch

        if special_char_found:
            fixed_pword = "{" + fixed_pword + "}"
        return fixed_pword

    def select_ref_data_pharm_and_health_care(self):
        """
        Select reference data for question
        :return:
        """
        query = "SELECT QuestionOption.Text, QuestionOption.Id FROM Question " + \
                "INNER JOIN QuestionOption ON Question.Id = QuestionOption.QuestionId " + \
                "WHERE QuestionOption.Text != 'options' " + \
                "AND Question.Text = 'User type'"

        return self.execute_query_fetchall(query, inspect.currentframe().f_code.co_name)

    def select_user_response_data(self, start_date, end_date):
        """
        Select reference data for question
        :return:
        """

        query = "SELECT UserQuestionnaire.Id, UserQuestionnaire.StartDate, " + \
                "UserResponse.TextAnswer, UserResponse.OptionId, QuestionnaireGroup.Name," + \
                "Person.FirstName, Person.LastName, Person.Email, Address.ZipCode " + \
                "FROM UserQuestionnaire " + \
                "INNER JOIN UserResponse ON UserQuestionnaire.Id = UserResponse.UserQuestionnaireId " + \
                "INNER JOIN Registrant ON UserQuestionnaire.RegistrantId = Registrant.Id " + \
                "INNER JOIN QuestionnaireGroup ON UserQuestionnaire.QuestionnaireId = QuestionnaireGroup.id " + \
                "INNER JOIN SystemUser ON Registrant.Id = SystemUser.id " + \
                "INNER JOIN Person ON SystemUser.id = Person.id " + \
                "INNER JOIN Address ON Person.id = Address.PersonId " + \
                "WHERE Registrant.ApplicationName = 'Commitment2Care.com Quiz' " + \
                "AND UserQuestionnaire.StartDate BETWEEN '<start_date>' AND '<end_date>' " + \
                "GROUP BY UserQuestionnaire.Id, UserQuestionnaire.StartDate, UserResponse.TextAnswer," + \
                "UserResponse.OptionId, QuestionnaireGroup.Name, Person.FirstName, Person.LastName," + \
                "Person.Email, Address.ZipCode ORDER BY MAX(UserQuestionnaire.StartDate) DESC"
        query = query.replace("<start_date>", start_date).replace("<end_date>", end_date)

        return self.execute_query_fetchall(query, inspect.currentframe().f_code.co_name)
