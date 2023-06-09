from typing import Dict

import pandas as pd


def compare_batsman_performances(
    batting_df: pd.DataFrame, batsman_name: str
) -> Dict[str, str]:
    """
    This function takes a pandas dataframe containing batting statistics for a cricket tournament and a batsman name,
    and compares the batsman's performance at home versus away matches.

    Args:
    - df: pandas dataframe containing batting statistics
    - batsman_name: string, the name of the batsman whose performance is to be compared

    Returns:
    - A dictionary containing the average runs scored, balls faced, strike rate, and batting strike rate for the batsman
    at home and away matches.
    """

    # Filter the dataframe to include only the specified batsman's data
    batsman_df = batting_df[batting_df["full_name"] == batsman_name]

    # Split the data into home and away matches
    batsman_team = batsman_df["current_innings"]
    home_df = batsman_df[batsman_df["home_team"] == batsman_team]
    away_df = batsman_df[batsman_df["away_team"] == batsman_team]

    # Calculate the average runs scored, balls faced, strike rate, and batting strike rate for home and away matches
    home_runs = home_df["runs"].mean()
    away_runs = away_df["runs"].mean()

    home_balls_faced = home_df["balls_faced"].mean()
    away_balls_faced = away_df["balls_faced"].mean()

    home_strike = home_df["strike_rate"].mean()
    away_strike = away_df["strike_rate"].mean()

    # Create a dictionary to store the results
    results = {
        "batsman_name": batsman_name,
        "home_runs_scored": home_runs,
        "away_runs_scored": away_runs,
        "home_balls_faced": home_balls_faced,
        "away_balls_faced": away_balls_faced,
        "home_strike_rate": home_strike,
        "away_strike_rate": away_strike,
    }

    return results


class BattingData:
    def __init__(self, batting_df: pd.DataFrame):
        self.batting_df = batting_df

    def get_all_performances(self):
        grouped = self.batting_df.groupby("full_name").agg(
            {
                "current_innings": lambda x: x.tail(1).iloc[0],
                "not_out": "sum",
                "runs": "sum",
                "balls_faced": "sum",
                "fours": "sum",
                "sixes": "sum",
                "strike_rate": "mean",
            }
        )

        # Calculate the batting average
        grouped = grouped.assign(batting_average=grouped["runs"] / grouped["not_out"])

        # Calculate boundary percentage for each player
        boundary_percentage = self.batting_df.groupby("full_name").apply(
            lambda x: ((x["fours"].sum() * 4) + (x["sixes"].sum() * 6))
            / x["runs"].sum()
            * 100
        )

        # Add boundary percentage to the grouped DataFrame
        grouped["boundary_percentage"] = boundary_percentage.values

        total_innings = self.batting_df.groupby("full_name").size()
        grouped["total_innings"] = total_innings

        # Rename the columns
        grouped.columns = [
            "team",
            "total_out",
            "total_runs",
            "total_balls",
            "total_fours",
            "total_sixes",
            "avg_strike_rate",
            "batting_average",
            "boundary_percentage",
            "total_innings",
        ]

        # Reset the index
        return grouped.reset_index().sort_values(by="total_runs", ascending=False)

    def best_batsman_per_game(self) -> pd.DataFrame:
        # create a new dataframe to store the best batsman in each game
        best_batsman_df = pd.DataFrame(columns=["match_id", "full_name", "runs"])

        # loop through each game in the data
        for match_id in self.batting_df["match_id"].unique():
            # subset the data to only include the current game
            game_data = self.batting_df[self.batting_df["match_id"] == match_id]

            # calculate the batting average for each batsman in the game
            batting_averages = game_data.groupby("full_name")["runs"].mean()

            # get the batsman with the highest batting average
            best_batsman = batting_averages.idxmax()

            # get the score of the best batsman
            score = game_data.loc[game_data["full_name"] == best_batsman, "runs"].sum()

            # add the best batsman and their score to the new dataframe
            new_row = {"match_id": match_id, "full_name": best_batsman, "runs": score}
            best_batsman_df = pd.concat(
                [best_batsman_df, pd.DataFrame(new_row, index=[0])], ignore_index=True
            )
        return best_batsman_df

    def compare_all_performances(self) -> pd.DataFrame:
        """
        This function takes a pandas dataframe containing batting statistics for a cricket tournament, loops over every
        unique batsman in the dataframe, and creates a new dataframe with the performances for every batsman.

        Args:
        - df: pandas dataframe containing batting statistics

        Returns:
        - A pandas dataframe containing the average runs scored, balls faced and batting strike rate for
        every batsman in the input dataframe, at home and away matches.
        """

        batsman_names = self.batting_df["full_name"].unique()

        results_list = []

        for batsman_name in batsman_names:
            batsman_results = compare_batsman_performances(
                self.batting_df, batsman_name
            )
            results_list.append(batsman_results)

        results_df = pd.DataFrame(results_list)

        return results_df
