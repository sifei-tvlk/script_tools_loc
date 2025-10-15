import json
import os
import pandas as pd


class UserInput:
    @staticmethod
    def choose_env():
        options = ["local", "staging", "production"]
        user_input = ""

        input_message = "Pick an option env:\n"

        for index, item in enumerate(options):
            input_message += f"{index + 1}) {item}\n"

        input_message += "Your choice: "

        while user_input not in map(str, range(1, len(options) + 1)):
            user_input = input(input_message)

        picked = options[int(user_input) - 1]

        print("You picked: " + picked)
        return picked

    @staticmethod
    def input_text(msg):
        input_message = f"Input {msg}: \n"
        input_txt = input(input_message)

        print(f'{msg} : {input_txt}')

        # input_lang_message = "Input language: \n"
        # input_lang = input(input_lang_message)
        #
        # print('lang {}'.format(input_lang))

        return input_txt

    @staticmethod
    def get_locgi_url(env):
        if env == 'staging':
            return "https://locgi.loc.stg-tvlk.cloud"
        elif env == 'production':
            return "https://locgi.loc.tvlk.cloud"
        elif env == 'local':
            # only for local testing purpose
            return ""
        else:
            raise Exception('cannot find the environment {}'.format(env))

    @staticmethod
    def get_locgs_url(env):
        if env == 'staging':
            return "https://locgs.loc.stg-tvlk.cloud"
        elif env == 'production':
            return "https://locgs.loc.tvlk.cloud"
        elif env == 'local':
            # only for local testing purpose
            return ""
        else:
            raise Exception('cannot find the environment {}'.format(env))

    @staticmethod
    def get_locrich_url(env):
        if env == 'staging':
            return "https://locrich.loc.stg-tvlk.cloud"
        elif env == 'production':
            return "https://locrich.loc.tvlk.cloud"
        elif env == 'local':
            # only for local testing purpose
            return ""
        else:
            raise Exception('cannot find the environment {}'.format(env))

    @staticmethod
    def get_srssrch_url(env):
        if env == 'staging':
            return "https://srssrch.srs.stg-tvlk.cloud"
        elif env == 'production':
            return "https://srssrch.srs.tvlk.cloud"
        elif env == 'local':
            # only for local testing purpose
            return ""
        else:
            raise Exception('cannot find the environment {}'.format(env))

    @staticmethod
    def load_checkpoint(checkpoint_path_file,
                        default_checkpoint):
        if os.path.exists(checkpoint_path_file):
            with open(checkpoint_path_file, "r") as f:
                return json.load(f)
        return default_checkpoint

    @staticmethod
    def save_checkpoint(checkpoint_path_file,
                        checkpoint):
        with open(checkpoint_path_file, "w") as f:
            json.dump(checkpoint, f, indent=2)

    @staticmethod
    def append_with_new_columns(new_row_dict, filename):
        # Wrap row in a DataFrame
        new_df = pd.DataFrame([new_row_dict])

        if os.path.exists(filename):
            # Load existing CSV
            existing_df = pd.read_csv(filename)

            # Combine old and new columns (union of both)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # Fill missing cells with NaN
            combined_df.to_csv(filename, index=False)
        else:
            # Write new file
            new_df.to_csv(filename, index=False)