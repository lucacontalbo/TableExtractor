from utils import init_args
from runnable import Runnable
from openai import OpenAIChatModel
from table_extraction import UnstructuredTableExtractor


if __name__ == "__main__":
    args = init_args()
    r = Runnable(args)
    s = r.run()
    print(s)
    