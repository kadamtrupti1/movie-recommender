"""Loads 50 sample movies. Runs automatically on first start, or manually: python seed.py"""
from urllib.parse import quote_plus
from models import db, Movie

# title | year | rating | genres | cast | description
DATA = """Inception|2010|8.8|Sci-Fi,Thriller,Action|Leonardo DiCaprio,Elliot Page|A thief enters dreams to plant an idea in a target's mind.
The Dark Knight|2008|9.0|Action,Crime,Drama|Christian Bale,Heath Ledger|Batman faces the Joker, a chaotic criminal mastermind in Gotham.
Interstellar|2014|8.7|Sci-Fi,Drama,Adventure|Matthew McConaughey,Anne Hathaway|Explorers travel through a wormhole to save humanity.
The Shawshank Redemption|1994|9.3|Drama|Tim Robbins,Morgan Freeman|A banker wrongly jailed forms a lasting friendship in prison.
Pulp Fiction|1994|8.9|Crime,Drama|John Travolta,Samuel L. Jackson|Interwoven stories of hitmen and a boxer in Los Angeles.
The Godfather|1972|9.2|Crime,Drama|Marlon Brando,Al Pacino|An aging mafia patriarch hands his empire to his reluctant son.
Forrest Gump|1994|8.8|Drama,Romance|Tom Hanks,Robin Wright|A kind man witnesses decades of American history.
The Matrix|1999|8.7|Sci-Fi,Action|Keanu Reeves,Laurence Fishburne|A hacker discovers reality is a simulation controlled by machines.
Gladiator|2000|8.5|Action,Drama,Adventure|Russell Crowe,Joaquin Phoenix|A betrayed Roman general seeks revenge as a gladiator.
Titanic|1997|7.9|Romance,Drama|Leonardo DiCaprio,Kate Winslet|A young couple falls in love aboard the doomed ship.
Avatar|2009|7.9|Sci-Fi,Adventure,Fantasy|Sam Worthington,Zoe Saldana|A marine joins the natives of the alien moon Pandora.
The Lion King|1994|8.5|Animation,Adventure,Drama|Matthew Broderick,Jeremy Irons|A lion prince flees his kingdom and returns to reclaim it.
Toy Story|1995|8.3|Animation,Comedy,Adventure|Tom Hanks,Tim Allen|Toys come alive and a cowboy doll rivals a space ranger.
Spirited Away|2001|8.6|Animation,Fantasy,Adventure|Rumi Hiiragi,Miyu Irino|A girl wanders into a spirit world and must save her parents.
Parasite|2019|8.5|Thriller,Drama,Comedy|Song Kang-ho,Choi Woo-shik|A poor family schemes its way into a wealthy household.
Joker|2019|8.4|Crime,Drama,Thriller|Joaquin Phoenix,Robert De Niro|A struggling comedian descends into madness in Gotham.
Avengers: Endgame|2019|8.4|Action,Sci-Fi,Adventure|Robert Downey Jr.,Chris Evans|The Avengers assemble to undo the destruction of the universe.
Iron Man|2008|7.9|Action,Sci-Fi,Adventure|Robert Downey Jr.,Gwyneth Paltrow|A billionaire builds a powered suit to fight evil.
Jurassic Park|1993|8.2|Adventure,Sci-Fi,Thriller|Sam Neill,Laura Dern|Cloned dinosaurs run wild at an island theme park.
Fight Club|1999|8.8|Drama,Thriller|Brad Pitt,Edward Norton|An insomniac and a soap salesman start an underground fight club.
Se7en|1995|8.6|Crime,Thriller,Drama|Brad Pitt,Morgan Freeman|Two detectives hunt a serial killer using the seven deadly sins.
The Silence of the Lambs|1991|8.6|Crime,Thriller,Drama|Jodie Foster,Anthony Hopkins|An FBI trainee seeks a cannibal's help to catch a killer.
Whiplash|2014|8.5|Drama,Music|Miles Teller,J.K. Simmons|A drummer faces an abusive teacher at a top music school.
La La Land|2016|8.0|Romance,Music,Drama|Ryan Gosling,Emma Stone|A pianist and an actress chase dreams and love in Los Angeles.
The Prestige|2006|8.5|Drama,Thriller,Sci-Fi|Christian Bale,Hugh Jackman|Two rival magicians battle to create the ultimate illusion.
Mad Max: Fury Road|2015|8.1|Action,Adventure,Sci-Fi|Tom Hardy,Charlize Theron|A rebel drives across a wasteland to escape a tyrant.
The Fellowship of the Ring|2001|8.8|Fantasy,Adventure,Drama|Elijah Wood,Ian McKellen|A hobbit sets out to destroy a powerful ring.
Harry Potter and the Sorcerer's Stone|2001|7.6|Fantasy,Adventure|Daniel Radcliffe,Emma Watson|A boy discovers he is a wizard and attends Hogwarts.
Finding Nemo|2003|8.2|Animation,Adventure,Comedy|Albert Brooks,Ellen DeGeneres|A clownfish crosses the ocean to find his lost son.
Coco|2017|8.4|Animation,Fantasy,Music|Anthony Gonzalez,Gael Garcia Bernal|A boy enters the Land of the Dead to find his musical ancestor.
Up|2009|8.3|Animation,Adventure,Comedy|Ed Asner,Jordan Nagai|An old man flies his house to South America with a boy scout.
The Notebook|2004|7.8|Romance,Drama|Ryan Gosling,Rachel McAdams|A poor man and a rich girl fall in love across social divides.
Pride and Prejudice|2005|7.8|Romance,Drama|Keira Knightley,Matthew Macfadyen|Elizabeth Bennet clashes with the proud Mr. Darcy.
The Hangover|2009|7.7|Comedy|Bradley Cooper,Zach Galifianakis|Three friends wake up after a bachelor party missing the groom.
Superbad|2007|7.6|Comedy|Jonah Hill,Michael Cera|Two teens try to buy alcohol for a high-school party.
3 Idiots|2009|8.4|Comedy,Drama|Aamir Khan,R. Madhavan|Three engineering students chase their dreams and friendship.
Dangal|2016|8.3|Drama,Sports|Aamir Khan,Fatima Sana Shaikh|A wrestler trains his daughters to become world champions.
Dilwale Dulhania Le Jayenge|1995|8.1|Romance,Drama,Comedy|Shah Rukh Khan,Kajol|Two young travelers fall in love in Europe and face family tradition.
Lagaan|2001|8.1|Drama,Sports,Adventure|Aamir Khan,Gracy Singh|Villagers play cricket against British rulers to cancel taxes.
Zindagi Na Milegi Dobara|2011|8.2|Comedy,Drama,Adventure|Hrithik Roshan,Farhan Akhtar|Three friends on a road trip in Spain rediscover life.
Baahubali: The Beginning|2015|8.0|Action,Fantasy,Adventure|Prabhas,Rana Daggubati|A young man learns of his royal lineage and fights for a kingdom.
RRR|2022|7.8|Action,Drama,Adventure|N.T. Rama Rao Jr.,Ram Charan|Two revolutionaries form a friendship while fighting British rule.
Get Out|2017|7.8|Horror,Thriller|Daniel Kaluuya,Allison Williams|A young man uncovers a disturbing secret at his girlfriend's family home.
A Quiet Place|2018|7.5|Horror,Thriller,Sci-Fi|Emily Blunt,John Krasinski|A family must live in silence to hide from deadly creatures.
The Conjuring|2013|7.5|Horror,Thriller|Vera Farmiga,Patrick Wilson|Paranormal investigators help a family terrorized by a dark presence.
Knives Out|2019|7.9|Crime,Comedy,Thriller|Daniel Craig,Ana de Armas|A detective investigates the death of a wealthy novelist.
Oppenheimer|2023|8.3|Drama,History,Thriller|Cillian Murphy,Emily Blunt|The story of the scientist behind the atomic bomb.
Dune|2021|8.0|Sci-Fi,Adventure,Drama|Timothee Chalamet,Zendaya|A noble heir protects a desert planet and its precious spice.
Spider-Man: Into the Spider-Verse|2018|8.4|Animation,Action,Adventure|Shameik Moore,Hailee Steinfeld|Teen Miles Morales becomes Spider-Man across many universes.
Black Panther|2018|7.3|Action,Sci-Fi,Adventure|Chadwick Boseman,Michael B. Jordan|A new king of Wakanda defends his nation from a rival."""


def seed():
    if Movie.query.count() > 0:
        return
    for i, line in enumerate(DATA.splitlines()):
        title, year, rating, genres, cast, desc = line.split("|")
        poster = f"https://placehold.co/300x450/2a1f3d/f5e9d3/png?text={quote_plus(title)}"
        db.session.add(Movie(title=title, year=int(year), rating=float(rating), genres=genres,
                             cast=cast, description=desc, poster_url=poster,
                             popularity=(i * 37) % 100))  # pseudo-random trending order
    db.session.commit()
    print("Seeded", Movie.query.count(), "movies")


if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed()
