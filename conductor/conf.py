from conductor.common import cartesian_product, tuplewise

import cerberus

CONF_SCHEMA = {'global': {},
               'runs': {}}

EXPERIMENT_SCHEMA = {'type': 'dict'}

# Functions to combine settings
COMBINATORS = {'cartesian-product': cartesian_product,
               'tuplewise': tuplewise}


def load_conf(conf_dict):
    """
    Validate and coerce a configuration dictionary

    Returns:
        errors (dict), conf (dict): a tuple of the validation errors (if
        any) and an empty dict for the configuration, or an empty dict
        of validation errors and the parsed configuration as a dict.
    """
    v = cerberus.Validator(CONF_SCHEMA,
                           ignore_none_values=False,
                           update=True,
                           allow_unknown=EXPERIMENT_SCHEMA)
    res = v.validated(conf_dict, normalize=True)
    if not res:
        return v.errors, {}
    else:
        global_settings = res.pop("global", {})
        runs = res.pop("runs", {})

        experiments = {}

        # Only experiments remain
        for name, settings in res.items():
            experiments[name] = global_settings.copy()
            global_environment = experiments[name].pop("environment", {})

            combine = settings.pop("combine")
            combinator = COMBINATORS[combine["with"]]
            command_template = settings.pop("command")
            args_templates = settings.pop("command-args")
            environment_template = settings.pop("environment")

            options = {}
            for option_key in combine['options']:
                option_values = settings.pop(option_key)
                options[option_key] = option_values

            commands = []

            for option_combination in combinator(options):
                combined_options = {**experiments[name], **settings}
                combined_options = {**combined_options, **option_combination}

                command = command_template.format(**combined_options)
                args = [arg.format(**combined_options) for arg in args_templates]

                local_environment = {key.format(**combined_options):
                                     val.format(**combined_options)
                                     for key, val in environment_template.items()}

                environment = {**global_environment, **local_environment}
                commands.append({'environment': environment,
                                 'command': command,
                                 'args': args})
            experiments[name]['commands'] = commands

            experiments[name] = {**experiments[name], **settings}

        return {'experiments': experiments,
                'runs': runs}, {}
