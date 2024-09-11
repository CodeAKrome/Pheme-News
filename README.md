# Pheme-News
Differentiate between mis/dis/mal-information in news using NLP to track actors and their interconnectivity with each other and world evens in a holistic fashion.
## Teaser
Love ahead by a nose.

![neo4jLoveHate](https://github.com/user-attachments/assets/305297f2-41a0-494f-83d2-dbcca0977a15)

This is using the same library as [flair-news](https://github.com/CodeAKrome/shed) in my shed.

---

# Sneak peek
I've uploaded sample.cypher.gz so you can play along at home.
This took an entire day to load. You might want to try `head sample.cypher` to make sure it works.

```
1505 news articles
ready to start consuming query after 18691584 ms
Added 28877 nodes, Created 144549 relationships, Set 320810 properties, Added 28768 labels
```

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

## This query will return the top 10 nodes with the highest bias, along with information about their LOVES and HATES relationships.

```cypher
MATCH (n)-[r:BIAS]->(m)
OPTIONAL MATCH (n)-[loves:LOVES]->(lovedNode)
OPTIONAL MATCH (n)-[hates:HATES]->(hatedNode)
RETURN n, r.bias AS biasScore, 
       collect(DISTINCT {type: 'LOVES', target: lovedNode}) AS lovesRelationships,
       collect(DISTINCT {type: 'HATES', target: hatedNode}) AS hatesRelationships
ORDER BY r.bias DESC
LIMIT 10
```

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

---

# Citations
## [flair](https://github.com/flairNLP/flair) framework:

```
@inproceedings{akbik2019flair,
  title={{FLAIR}: An easy-to-use framework for state-of-the-art {NLP}},
  author={Akbik, Alan and Bergmann, Tanja and Blythe, Duncan and Rasul, Kashif and Schweter, Stefan and Vollgraf, Roland},
  booktitle={{NAACL} 2019, 2019 Annual Conference of the North American Chapter of the Association for Computational Linguistics (Demonstrations)},
  pages={54--59},
  year={2019}
}

```
## [NewsMTSC](https://github.com/fhamborg/NewsMTSC?tab=readme-ov-file)
### [paper](https://aclanthology.org/2021.eacl-main.142/) ([PDF](https://aclanthology.org/2021.eacl-main.142.pdf)):

```
@InProceedings{Hamborg2021b,
  author    = {Hamborg, Felix and Donnay, Karsten},
  title     = {NewsMTSC: (Multi-)Target-dependent Sentiment Classification in News Articles},
  booktitle = {Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2021)},
  year      = {2021},
  month     = {Apr.},
  location  = {Virtual Event},
}
```