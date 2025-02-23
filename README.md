# Still Work in Progress! early version

Use Datafix to create a validation pipeline to ensure correct data, and help the user find & clean up bad data.  
Great for asset validation in a game-dev pipeline.

worflow:
1. collect datanodes (e.g. meshes, materials, textures)
2. validate your DataNodes, saving the validation outcome (SUCCESS, WARN, FAIL) in resultNodes
3. create a report, or use UI to see the outcome.

features:
- all nodes are linked to easily query each other for advanced pipelines.
- modular to enable reusable nodes for multiple pipelines. or reuse actions between nodes.
- support headless mode, completely de-coupled from the UI
- open source, easy to extend.
- dcc-independent. can run in any app, or standalone.


|Console |UI |
|--|--|
![image](https://github.com/user-attachments/assets/27622962-97ca-45f7-9784-47fda764a7f2) |![image](https://github.com/user-attachments/assets/2fd3e1d9-e92f-496e-961f-0efbfc763309) | 
