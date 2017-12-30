from conductor.common import cartesian_product, tuplewise
from conductor.run_experiments import ALLOWED_COLLATE_METHODS

import cerberus
import daiquiri
import jinja2

log = daiquiri.getLogger()

CONF_SCHEMA = {'global': {'type': 'dict'},
               'runs': {'type': 'dict'}}

EXPERIMENT_SCHEMA = {'type': 'dict',
                     # These are option combinations
                     'allow_unknown': {'oneof': [{'type': 'list',
                                                  'minlength': 1},
                                                 {'type': 'string'}]},
                     'schema': {'collate-with':
                                {'type': 'string',
                                 'allowed': ALLOWED_COLLATE_METHODS,
                                 'default': 'first',
                                 'required': True},
                                'command':
                                {'type': 'string',
                                 'required': True},
                                'command-args':
                                {'type': 'list',
                                 'default': [],
                                 'required': True},
                                'die-on-timeout':
                                {'type': 'boolean',
                                 'default': True,
                                 'required': True},
                                'nrounds':
                                {'type': 'integer',
                                 'default': 1,
                                 'required': False},
                                'run-at-least':
                                {'type': 'integer',
                                 'default': 1,
                                 'required': False},
                                'override-settings':
                                {'type': 'list',
                                 'default': [],
                                 # FIXME validate members
                                 'required': False},
                                'start':
                                {'type': 'integer',
                                 'default': 1,
                                 'required': False},
                                'stop':
                                {'type': 'integer',
                                 'default': 1,
                                 'required': False},
                                'step-size':
                                {'type': 'integer',
                                 'default': 1,
                                 'required': False},
                                'timeout-ms':
                                {'type': 'integer',
                                 'default': 1,
                                 'required': False},
                                'combine':
                                {'type': 'dict',
                                 # Fixme: validate members
                                 'required': False},
                                'environment':
                                {'type': 'dict',
                                 'required': False},
                                'capture':
                                {'type': 'dict',
                                 'default': {},
                                 # FIXME validate members
                                 'required': False},
                     }
}

# Functions to combine settings
COMBINATORS = {'cartesian-product': cartesian_product,
               'tuplewise': tuplewise}

def handle_template(output, templ_heading):
    if templ_heading in output:
        output[templ_heading] = jinja2.Template(output[templ_heading])


def load_conf(conf_dict):
    """
    Validate and coerce a configuration dictionary

    Returns:
        errors (dict), conf (dict): a tuple of the validation errors (if
        any) and an empty dict for the configuration, or an empty dict
        of validation errors and the parsed configuration as a dict.
    """
    v = cerberus.Validator(CONF_SCHEMA,
                           ignore_none_values=True,
                           update=True,
                           allow_unknown=EXPERIMENT_SCHEMA)
    res = v.validated(conf_dict, normalize=True, update=True)
    if not res:
        return v.errors, {}
    else:
        global_settings = res.pop("global", {})
        runs = res.pop("runs", {})

        for run_name, run_content in runs.items():
            log.info("Compiling templates for %s", run_name)
            outputs = run_content.get("output")

            for output in outputs:
                for field in ['heading', 'row-format', 'file', 'label']:
                    handle_template(output, field)


        experiments = {}

        # Only experiments remain
        for name, settings in res.items():
            experiments[name] = global_settings.copy()
            global_environment = experiments[name].pop("environment", {})

            combine = settings.pop("combine")
            combinator = COMBINATORS[combine["with"]]
            command_template = settings.pop("command")
            args_templates = settings.pop("command-args")
            environment_template = settings.pop("environment", {})

            override_settings = settings.pop("override-settings", {})

            options = {}
            for option_key in combine['options']:
                option_values = settings.pop(option_key)

                # special case: a range expression
                if isinstance(option_values, str):
                    start, stop, step = [int(i) for i in option_values.split(":")]
                    option_values = list(range(start, stop + 1, step))

                options[option_key] = option_values

            commands = []

            for option_combination in combinator(options):
                combined_options = {**experiments[name], **settings}
                combined_options = {**combined_options, **option_combination}

                command_settings = settings.copy()

                for option, value in option_combination.items():
                    for override in override_settings:
                        if override['option'] == option \
                           and override['value'] == value:
                            log.debug("Using override options for %s=%s: for settings %s",
                                      option, value,
                                      ", ".join(override['settings'].keys()))
                            command_settings = {**command_settings,
                                                **override['settings']}
                            combined_options = {**combined_options,
                                                **override['settings']}

                command = command_template.format(**combined_options)
                args = [arg.format(**combined_options) for arg in args_templates]

                local_environment = {key.format(**combined_options):
                                     val.format(**combined_options)
                                     for key, val in environment_template.items()}

                environment = {**global_environment, **local_environment}
                commands.append({'environment': environment,
                                 'command': command,
                                 'args': args,
                                 'option-combination': option_combination,
                                 'settings': command_settings})

            experiments[name]['commands'] = commands

        return {}, {'experiments': experiments,
                    'runs': runs}
