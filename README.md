# Pheme-News
Differentiate between mis/dis/mal-information in news using NLP to track actors and their interconnectivity with each other and world evens in a holistic fashion.
## Teaser
Love ahead by a nose.

![neo4jLoveHate](https://github.com/user-attachments/assets/305297f2-41a0-494f-83d2-dbcca0977a15)

---

# Sneak peek
I've uploaded sample.cypher.gz so you can play along at home.
This took an entire day to load. You might want to try `head sample.cypher` to make sure it works.

- Gunzip
```sh
gunzip sample.cypher.gz
```
- The user is set to neo4j, set the password
```sh
export NEO4J_PASS='state your password'
```
- Run the docker container.
```sh
make neo4j
```
- Load the sample. This might literally take all day.
```sh
make sampleload
```

---

# Some things I've run

## Top 10 connected
```cypher
MATCH (n)
WITH n, COUNT{(n)--() } AS connectionCount
RETURN n, connectionCount
ORDER BY connectionCount DESC
LIMIT 10
```

## Top 10 connected person
```cypher
MATCH (n:PERSON)
WITH n, COUNT{ (n)--() } AS connectionCount
RETURN n, connectionCount
ORDER BY connectionCount DESC
LIMIT 10
```

## Select node and all connected nodes for work of art
```cypher
MATCH (n:WORK_OF_ART)
WHERE n.val IN ["Beetlejuice Beetlejuice", "Beetlejuice"]
MATCH (n)-[r]-(connected)
RETURN n, r, connected
```

## Most connected
```cypher
MATCH (n:PERSON)
WITH n, COUNT{ (n)--() } AS connectionCount
RETURN n, connectionCount
ORDER BY connectionCount DESC
LIMIT 20
```
## Love Hate

```cypher
MATCH (n)-[r:LOVES|HATES]->(m) RETURN n, type(r), m
```
This will return the source node, the relationship type (LOVES or HATES), and the target node.

## Create user

```cypher
create user kyle if not exists set plaintext password "stupidpassword" change not required
```

## Delete everything

```cypher
MATCH (n) DETACH DELETE n
```

## Import cypher commands
```sh
bin/cypher-shell -u neo4j -p "password" -f scripts/movies.cypher [-d "database"]
```

## Return all nodes

```cypher
MATCH (n) MATCH ()-[r]->() RETURN n, r
```

```cypher
MATCH (n) RETURN (n)
```

## Other good way for get ALL nodes (and nodes without relationship) :

```cypher
MATCH (n) RETURN n UNION START n = rel(*) return n;
```

