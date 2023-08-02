from datetime import datetime

import faker

from factory import Factory

from app.schemas.projects import ProjectCreate, PatchProjectUpdateRequest

fake = faker.Faker()


class ProjectCreateFactory(Factory):
    class Meta:
        model = ProjectCreate

    name = fake.company()
    members = [fake.uuid4(), fake.uuid4(), fake.uuid4()]
    sites = [fake.domain_name(), fake.domain_name(), fake.domain_name()]
    activity_types = ["some", "some1", "some2"]
    country = fake.city()
    region = "Minsk region"
    social_networks = [fake.company(), fake.company(), fake.company()]


class ProjectUpdateFactory(Factory):
    class Meta:
        model = PatchProjectUpdateRequest

    name = fake.company()
    members = [fake.uuid4(), fake.uuid4(), fake.uuid4()]
    sites = [fake.domain_name(), fake.domain_name(), fake.domain_name()]


class ProjectGetFactory(ProjectCreateFactory):
    created_at = datetime
    owner = "1"

