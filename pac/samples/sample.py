from pac.port import *


session = Session()
session.registered_plugins.append(CollectHelloWorld)
session.registered_plugins.append(CollectHelloWorldList)
session.registered_plugins.append(ValidateHelloWorld)
session.run()

print()
# print validation results instances
for plugin in session.plugin_instances:
    print(plugin)
    print(plugin.children)
    for inst in plugin.children:
        print('STATE', inst, inst.parent, inst.parent.state)  # TODO get validation state, atm we get parent(collect) state



