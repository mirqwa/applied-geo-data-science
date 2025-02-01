import pulp


if __name__ == "__main__":
    patients = 150
    medical_centers = 4
    service_area = 5500

    patient_seed = 54321
    medical_centers_seed = 54321

    solver = pulp.PULP_CBC_CMD(msg=False, warmStart=True)
