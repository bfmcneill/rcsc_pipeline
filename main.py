from typing import List, Dict
from collections import OrderedDict
import pathlib
from loguru import logger
import praw
from tinydb import TinyDB


def process_comment(c, submission_id):
    """Parse Reddit comment data

    Args:
        c (praw.models.reddit.comment.Comment): comment data
        submission_id (str): comment submission identifier

    Returns:
        OrderedDict
    """

    return OrderedDict(
        comment_id=c.id,
        submission=submission_id,
        author_id=c.author.id,
        author_name=c.author.name,
        author_verified=c.author.verified,
        body=c.body,
        created_utc=c.created_utc,
        depth=c.depth,
        downs=c.downs,
        edited=c.edited,
        is_root=c.is_root,
        is_submitter=c.is_submitter,
        likes=c.likes,
        parent_id=c.parent_id,
        score=c.score,
        total_awards_received=c.total_awards_received,
        ups=c.ups,
    )


def process_submission(s):
    """Parse Reddit submission data

    Args:
        s (praw.models.reddit.submission.Submission): submission data

    Returns:
        OrderedDict
    """

    return OrderedDict(
        submission_id=s.id,
        title=s.title,
        score=s.score,
        url=s.url,
        created_utc=s.created_utc,
        author_id=s.author.id,
        author_name=s.author.name,
        author_verified=s.author.verified,
        link_flare_text=s.link_flair_text,
        upvote_ratio=s.upvote_ratio,
    )


def destroy_db():
    """Destroy local storage

    Returns:
        None
    """
    logger.debug("destroying db.json")
    dbjson_path = pathlib.Path.cwd() / "db.json"
    dbjson_path.unlink(missing_ok=True)


def init_db(db_path='db.json'):
    """Initialize local storage

    Returns:
        Tuple(tinydb.table.Table, tinydb.table.Table)
    """
    db = TinyDB(db_path)
    logger.debug("database initialized")

    comments_tb = db.table("comment_tb")
    submissions_tb = db.table("submission_tb")
    return comments_tb, submissions_tb


def authenticate_reddit_client():
    """Create Reddit client

    Returns:
        praw.reddit.Reddit
    """
    reddit = praw.Reddit("bot1", config_interpolation="basic")
    reddit.read_only = True
    logger.info(f"authenticated as : {reddit.user.me()}")
    return reddit


def entrypoint(subreddit_name):
    """Entrypoint

    Returns:
        None
    """
    # local storage actions
    destroy_db()
    comments_tb, submissions_tb = init_db()

    reddit = authenticate_reddit_client()

    # create pointer to specific subreddit
    subreddit = reddit.subreddit(subreddit_name)
    logger.info(f"reading newest submissions in : {subreddit.display_name}")

    # process subreddit submissions and comments
    process_submissions(comments_tb, submissions_tb, subreddit)




def process_submissions(comments_tb, submissions_tb, subreddit, limit=10):
    """Process reddit submissions and it's comments forrest

    Args:
        comments_tb (tinydb.table.Table): db table reference
        submissions_tb (tinydb.table.Table): db table reference
        subreddit (str): the subreddit name
        limit (int): amount of subreddit submissions to process

    Returns:
        None
    """
    logger.debug(f"begin processing {limit} newest submissions")

    for s in subreddit.new(limit=10):
        logger.debug(f"loading submission: {s.id}")
        submission: Dict = process_submission(s)

        s.comment_sort = "new"
        s.comments.replace_more(limit=None)

        logger.debug(f"loading comments for submission: {s.id}")
        comments: List[Dict] = [
            process_comment(c, submission["submission_id"]) for c in s.comments.list()
            if '**user report**' not in c.body.lower()
        ]

        logger.debug("inserting submission")
        submissions_tb.insert(submission)

        logger.debug(f"inserting {len(comments)} comments")
        comments_tb.insert_multiple(comments)


if __name__ == "__main__":
    # entrypoint(subreddit_name="wallstreetbets")
    entrypoint(subreddit_name="worldnews")
    logger.debug("end of process")
