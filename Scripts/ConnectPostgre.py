import psycopg2


def connect():
    conn = psycopg2.connect(
        host='145.74.104.145',
        database='postgres',
        user='j3_g10',
        password='Blaat1234',
        port=5432
    )
    return conn, conn.cursor()


def getcsv():
    """
    Get the csv file containing the health data of a person
    :return:
    """
    health_data = {}
    keys = False
    with open('../../Data/person1.csv') as file:
        for line in file.readlines():
            line = line.strip().split(',')
            if keys:
                key = line
                keys = False
            elif line[0] != '':
                if len(line) < 2:
                    keys = True
                else:
                    for i in range(len(key)):
                        if health_data.get(key[i]) is not None:
                            if line[i] not in health_data[key[i]]:
                                health_data[key[i]].append(line[i])
                        else:
                            health_data[key[i]] = [line[i]]
    return health_data


def getvcf():
    """
    Get the 10 missense/frameshift variants from chr 21 from a person
    :return:
    """
    pass


def insert_health_data(cur, health_data, person_id):
    """
    Inserts a persons health data into the database
    :param health_data:
    :param cur:
    :param person_id:
    :return:
    """
    # Check if person is in database
    cur.execute("""SELECT person_id FROM person
                WHERE person_source_value like %s""",
                (health_data['Participant'][0],))
    response = cur.fetchone()

    if response is not None:
        exit("This person is already in the database")

    # “Participant”, “Birth month”, “Birth year”, “Sex”, “Ethnicity” en “Conditions or Symptoms”
    sex = 0
    if health_data['Sex'][0] == 'M':
        sex = 1
    elif health_data['Sex'][0] == 'F':
        sex = 2

    # cur.execute("""INSERT INTO person(person_id, person_source_value,
    #                                 gender_concept_id, gender_source_value,
    #                                 year_of_birth, month_of_birth,
    #                                 ethnicity_concept_id, ethnicity_source_value,
    #                                 race_concept_id
    #                                 ) VALUES (%s, %s,
    #                                 %s, %s,
    #                                 %s, %s,
    #                                 %s, %s,
    #                                 %s)""",
    #                                 (person_id, health_data['Participant'][0],
    #                                  sex, health_data['Sex'][0],
    #                                  health_data['Birth year'][0], health_data['Birth month'][0],
    #                                  [hier moet race concept id in type int], health_data['Ethnicity'][0],
    #                                  0
    # ))

    conditions = []
    if health_data.get('Conditions or Symptom') is not None:
        conditions.extend(health_data['Conditions or Symptom'])
    if health_data.get('Allergies') is not None:
        conditions.extend(health_data['Allergies'])

    condition_id = get_occurrence_id(cur)

    # for condition in conditions:
    #     cur.execute("""INSERT INTO condition_occurrence(condition_occurrence_id, person_id,
    #                                                     condition_type_concept_id,
    #                                                     condition_concept_id, condition_source_value,
    #                                                     condition_start_date
    #                                                     ) VALUES (%s, %s,
    #                                                     %s,
    #                                                     %s, %s,
    #                                                     %s)""",
    #                                                     (condition_id, person_id,
    #                                                      0,
    #                                                      [hier moet condition concept id in type int], condition,
    #                                                      '0001-01-01'))
    #     condition_id += 1

    # https://ohdsi.github.io/CommonDataModel/cdm531.html#CONDITION_OCCURRENCE


def insert_snp_data(cur, snps, person_id):
    """
    Inserts a persons snp data into the databse
    :param cur:
    :param snps:
    :param person_id:
    :return:
    """
    measurement_id = get_measurement_id(cur)

    with open('../1503AHX-0002_PGPC-0030-243898-U_SNP_INDEL.vcf', 'r') as file:
        while "startTime" not in (line := file.readline()):
            pass
    print(line)
    months = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }
    measurement_datetime = line.split('=')[1].split(' ')
    date = f'{measurement_datetime[4]}-{months[measurement_datetime[1]]}-{measurement_datetime[2]}'
    time = measurement_datetime[3]
    date_time = f'{date} {time}'

    for snp in snps:
        cur.execute("""INSERT INTO measurement( measurement_id,
                                                person_id,
                                                measurement_concept_id,
                                                measurement_date,
                                                measurement_datetime,
                                                measurement_time,
                                                


                                                ) VALUES (%s, %s,
                                                %s,
                                                %s, %s,
                                                %s)""",
                                                (condition_id, person_id,
                                                 0,
                                                 [hier moet condition concept id in type int], condition,
                                                 '0001-01-01'))


def get_person_id(cur):
    cur.execute('SELECT person_id FROM person '
                'ORDER BY person_id DESC '
                'LIMIT 1')

    response = cur.fetchone()
    if response is None:
        return 0
    return response[0] + 1


def get_occurrence_id(cur):
    cur.execute('SELECT condition_occurrence_id FROM condition_occurrence '
                'ORDER BY condition_occurrence_id DESC '
                'LIMIT 1')

    if (response := cur.fetchone()) is None:
        return 0
    return response[0] + 1


def get_measurement_id(cur):
    cur.execute('SELECT measurement_id FROM measurement '
                'ORDER BY measurement_id DESC '
                'LIMIT 1')

    return 0 if (response := cur.fetchone()) is None else response[0] + 1


def main():
    conn, cur = connect()

    health = getcsv()
    snps = getvcf()

    person_id = get_person_id(cur)

    insert_health_data(cur, health, person_id)
    insert_snp_data(cur, snps, person_id)


    # sql = """INSERT INTO vendors(vendor_name)     # voorbeeld sql statement voor in tabel zetten
    #       VALUES(%s) RETURNING vendor_id;"""
    # cur.execute(sql, (value1, value2))            # data in database zetten
    # cur.commit()                                  # permanently changes database

    # respone = cur.fetchone()
    # respone = cur.fetchmany(size=4)
    # respone = cur.fetchall()

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()


# source value = waarde in data (wat in pdf staat)
# andere values = waarde van OMOP