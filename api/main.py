from app import app, api
from resources import AnimalsResource, AnimalResource, \
    CentersResource, CenterResource, SpeciesResource, \
    SpecieResource, RegisterResource, LoginResource

# Register API resources
api.add_resource(AnimalsResource, "/animals", "/animals/")
api.add_resource(AnimalResource, "/animals/<int:animal_id>",
                 "/animals/<int:animal_id>/")
api.add_resource(CentersResource, "/centers", "/centers/")
api.add_resource(CenterResource, "/centers/<int:center_id>",
                 "/centers/<int:center_id>/")
api.add_resource(SpeciesResource, "/species", "/species/")
api.add_resource(SpecieResource, "/species/<int:specie_id>",
                 "/species/<int:specie_id>/")
api.add_resource(RegisterResource, "/register", "/register/")
api.add_resource(LoginResource, "/login", "/login/")

if __name__ == "__main__":
    # Run app
    app.run()
