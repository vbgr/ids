import datetime
import uuid

import genids



T = 1000000


def test_uuid_generation(t: int) -> None:
    started = datetime.datetime.now()
    for i in range(T):
        _ = uuid.uuid4()
    finished = datetime.datetime.now()
    print(f"{T} uuids v4 generated in {finished - started}")



def test_rsa_ids_generation(t: int) -> None:
    started = datetime.datetime.now()
    for i in range(T):
        _ = genids.encode(genids.encrypt(i))
    finished = datetime.datetime.now()
    print(f"{T} rsa ids generated in {finished - started}")


test_uuid_generation(T)

genids.E = 127
genids.D = pow(genids.E, -1, genids.N)

test_rsa_ids_generation(T)

genids.E = 65537
genids.D = pow(genids.E, -1, genids.N)

test_rsa_ids_generation(T)

genids.E = 1148399797
genids.D = pow(genids.E, -1, genids.N)

test_rsa_ids_generation(T)

genids.E = 1948399795
genids.D = pow(genids.E, -1, genids.N)

test_rsa_ids_generation(T)
