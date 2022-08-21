from pac.port import *


class CollectHelloWorld(Collector):
    def _run(self):
        return ["Hello World"]


class ValidateSuccess(Validator):
    def validate_instance(self, instance):
        pass


class ValidateFail(Validator):
    def validate_instance(self, instance):
        raise Exception('Fail')


def main():
    session = Session()
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(ValidateFail)
    session.registered_plugins.append(ValidateSuccess)
    session.run()

    # if we first succeed, then fail validation, then instance wrap state should fail
    assert session.plugin_instances[0].instance_wrappers[0].state != 'success'

    session.pp_tree()


if __name__ == '__main__':
    main()
