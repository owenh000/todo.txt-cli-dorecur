#!/usr/bin/env python3
# A todo.txt-cli add-on for recurring tasks
# Copyright 2021 Owen T. Heisler. GNU General Public License, version 3.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Mark task(s) as done, adding new task(s) if required for recurrence."""

import argparse
import calendar
import datetime
import os
import re
import subprocess
import sys


def add_new_task(line):
    """Add a new task by running todo-txt *add*."""
    subprocess.run(
        [os.environ['TODO_FULL_SH'], 'command', 'add', line],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def adjust_date(date, adjust):
    """Return adjusted date, ignoring the `+` prefix if it exists.

    If the date is None, return None.

    >>> adjust_date(datetime.date(1970, 1, 1), '1')
    datetime.date(1970, 1, 2)
    >>> adjust_date(datetime.date(1970, 1, 1), '+1')
    datetime.date(1970, 1, 2)
    >>> adjust_date(datetime.date(1970, 1, 1), '1d')
    datetime.date(1970, 1, 2)
    >>> adjust_date(datetime.date(1970, 1, 1), '1b')
    datetime.date(1970, 1, 2)
    >>> adjust_date(datetime.date(1970, 1, 1), '2b')
    datetime.date(1970, 1, 5)
    >>> adjust_date(datetime.date(1970, 1, 1), '2w')
    datetime.date(1970, 1, 15)
    >>> adjust_date(datetime.date(1970, 1, 1), '3m')
    datetime.date(1970, 4, 1)
    >>> adjust_date(datetime.date(1970, 1, 31), '2m')
    datetime.date(1970, 3, 31)
    >>> adjust_date(datetime.date(1970, 1, 31), '1m')
    datetime.date(1970, 2, 28)
    >>> adjust_date(datetime.date(1970, 1, 1), '4y')
    datetime.date(1974, 1, 1)

    """
    if date is None:
        return None
    m = re.fullmatch(r'(\+?)(\d+)([dbwmy]?)', adjust)
    if not m:
        raise Exception('Malformed `rec:` value')
    num = int(m.group(2))
    unit = m.group(3)
    if unit in ['', 'd']:
        # Add days
        return date + datetime.timedelta(days=num)
    elif unit == 'b':
        # Add business days
        while num > 0:
            date += datetime.timedelta(days=1)
            weekday = date.weekday()
            if weekday >= 5:
                continue
            num -= 1
        return date
    elif unit == 'w':
        # Add weeks
        return date + datetime.timedelta(weeks=num)
    elif unit == 'm':
        # Add months
        month = date.month - 1 + num
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)
    elif unit == 'y':
        # Add years
        return date.replace(year=(date.year + num))


def get_date(line, key):
    """Return the date given in the specified key.

    Return None if the key does not exist.

    >>> get_date('Test task t:1970-01-01', 't')
    datetime.date(1970, 1, 1)
    >>> get_date('Test task', 't')
    >>> get_date('Test task t:malformed', 't')
    Traceback (most recent call last):
        ...
    Exception: Malformed `t:` date
    >>> get_date('Test task due:1970-01-01', 'due')
    datetime.date(1970, 1, 1)
    >>> get_date('Test task', 'due')
    >>> get_date('Test task due:malformed', 'due')
    Traceback (most recent call last):
        ...
    Exception: Malformed `due:` date

    """
    value = get_key_value(line, key)
    if value is None:
        return None
    else:
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            raise Exception('Malformed `{}:` date'.format(key))


def get_key_value(line, key):
    """Return the value of key as a string, or None if it does not exist.

    Raise an Exception if the key is specified more than once.

    >>> get_key_value('Test task', 'key')
    >>> get_key_value('Test task key:val', 'key')
    'val'
    >>> get_key_value('key:val Test task', 'key')
    'val'
    >>> get_key_value('Test task key:val1 key:val2', 'key')
    Traceback (most recent call last):
        ...
    Exception: Task has multiple `key:` keys
    >>> get_key_value('Test task rec:1', 'rec')
    '1'
    >>> get_key_value('(A) Test task rec:3d', 'rec')
    '3d'

    """
    matches = re.findall(r'(?:^| ){}:([^ ]*)'.format(key), line)
    count = len(matches)
    if count == 1:
        return matches[0].lstrip(' ')
    elif count == 0:
        return None
    else:
        raise Exception('Task has multiple `{}:` keys'.format(key))


def get_line(item_number):
    """Get task by number and return as string."""
    with open(os.environ['TODO_FILE']) as f:
        for i, line in enumerate(f):
            if i+1 == item_number:
                return line.rstrip('\n')
    raise Exception('Task {} does not exist'.format(item_number))


def make_new_task(line, now=datetime.date.today()):
    """Replace dates in line and return new line.

    >>> now = datetime.date(1970, 1, 3)
    >>> make_new_task('Test task', now)
    >>> make_new_task('Test task rec:3d', now)
    'Test task rec:3d'
    >>> make_new_task('1970-01-01 Test task rec:3d', now)
    'Test task rec:3d'
    >>> make_new_task('(A) 1970-01-01 Test task rec:3d', now)
    '(A) Test task rec:3d'
    >>> make_new_task('Test task rec:+3d', now)
    'Test task rec:+3d'
    >>> make_new_task('Test task t:1970-01-01 rec:3d', now)
    'Test task t:1970-01-06 rec:3d'
    >>> make_new_task('Test task t:1970-01-01 rec:+3d', now)
    'Test task t:1970-01-04 rec:+3d'
    >>> make_new_task('Test task due:1970-01-01 rec:3d', now)
    'Test task due:1970-01-06 rec:3d'
    >>> make_new_task('Test task due:1970-01-01 rec:+3d', now)
    'Test task due:1970-01-04 rec:+3d'
    >>> make_new_task('Test task t:1970-01-01 due:1970-01-05 rec:3d', now)
    'Test task t:1970-01-06 due:1970-01-10 rec:3d'
    >>> make_new_task('Test task t:1970-01-01 due:1970-01-05 rec:+3d', now)
    'Test task t:1970-01-04 due:1970-01-08 rec:+3d'
    >>> make_new_task('Test task rec:1 rec:2', now)
    Traceback (most recent call last):
        ...
    Exception: Task has multiple `rec:` keys
    >>> make_new_task('Test task t:1970-01-01 t:1970-01-02, rec:1m', now)
    Traceback (most recent call last):
        ...
    Exception: Task has multiple `t:` keys
    >>> make_new_task('Test task due:1970-01-01 due:1970-01-02 rec:1', now)
    Traceback (most recent call last):
        ...
    Exception: Task has multiple `due:` keys

    # README examples
    >>> make_new_task('Fix lamp')
    >>> make_new_task('Meet friend for tea rec:1')
    'Meet friend for tea rec:1'
    >>> now = datetime.date(2021, 1, 2)
    >>> make_new_task('Water flowers t:2021-01-01 rec:5d', now)
    'Water flowers t:2021-01-07 rec:5d'
    >>> make_new_task('Send birthday greeting to friend t:2021-04-04 rec:+1y')
    'Send birthday greeting to friend t:2022-04-04 rec:+1y'
    >>> make_new_task('Pay rent t:2021-01-28 due:2021-02-01 rec:+1m')
    'Pay rent t:2021-02-28 due:2021-03-01 rec:+1m'
    >>> now = datetime.date(2021, 1, 3)
    >>> old_task = 'Do offline backup t:2021-01-01 due:2021-01-08 rec:2w'
    >>> make_new_task(old_task, now)
    'Do offline backup t:2021-01-17 due:2021-01-24 rec:2w'
    >>> now = datetime.date(2021, 1, 31)
    >>> make_new_task('Get groceries t:2021-01-14 rec:1m', now)
    'Get groceries t:2021-02-28 rec:1m'
    >>> make_new_task('Pay rent t:2021-01-31 due:2021-02-01 rec:+1m')
    'Pay rent t:2021-02-28 due:2021-03-01 rec:+1m'

    """
    adjustment = get_key_value(line, 'rec')
    if adjustment is None:
        return None
    start_date = get_date(line, 't')
    due_date = get_date(line, 'due')
    if not start_date and not due_date:
        # Neither date is specified
        return line
    elif start_date and due_date:
        if adjustment.startswith('+'):
            # Both dates are specified, with strict recurrence
            # Original + adjustment for both dates
            start_date = adjust_date(start_date, adjustment)
            due_date = adjust_date(due_date, adjustment)
        else:
            # Both dates are specified, with normal recurrence
            offset = due_date - start_date
            # Today + adjustment for start date
            start_date = adjust_date(now, adjustment)
            # Today + offset for due date
            due_date = start_date + offset
    elif adjustment.startswith('+'):
        # Only one date is specified, with strict recurrence.
        # Original + adjustment for whichever date is specified
        start_date = adjust_date(start_date, adjustment)
        due_date = adjust_date(due_date, adjustment)
    else:
        # Only one date is specified, with normal recurrence.
        # Today + adjustment for whichever date is specified
        if start_date:
            start_date = adjust_date(now, adjustment)
        if due_date:
            due_date = adjust_date(now, adjustment)
    # Apply date changes
    if start_date:
        line = set_key_value(line, 't', start_date.isoformat())
    if due_date:
        line = set_key_value(line, 'due', due_date.isoformat())
    return line


def mark_done(item_number):
    """Mark task as complete by executing todo-txt *do* action."""
    subprocess.run(
        [os.environ['TODO_FULL_SH'], 'command', 'do', str(item_number)],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def parse_args():
    p = argparse.ArgumentParser(
        add_help=False,
        description=globals()['__doc__'],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subp = p.add_subparsers(title='actions', dest='action', required=True)
    usage = subp.add_parser('usage')
    usage = subp.add_parser('test')
    do = subp.add_parser('do')
    do.add_argument('item', type=int, nargs='+', metavar='ITEM#',
                    help='The task number')
    return p.parse_args()


def set_key_value(line, key, value):
    """Set value of key and return new line.

    A value of None deletes the key and its value.

    This does not check for duplicate keys; that is done by
    get_key_value().

    >>> set_key_value('Test task', 'key', 'val')
    'Test task key:val'
    >>> set_key_value('Test task key:val1 b key2:val2', 'key', 'val')
    'Test task key:val b key2:val2'
    >>> set_key_value('Test task key:val', 'key', None)
    'Test task'

    """
    if value is None:
        space = ''
        replacement = ''
    else:
        space = r'\1'
        replacement = '{}:{}'.format(key, value)
    line, repl_count = re.subn(r'(^| ){}:[^ ]*'.format(key),
                               space + replacement, line)
    if repl_count == 0:
        line += ' ' + replacement
    return line


def usage():
    """Return usage text suitable for todo-txt."""
    text = """
    do ITEM#[, ITEM#, ITEM#, ...]
      Mark ITEM# as complete. If `rec:` is set, add a new task, updating
      any start/due dates based on the value of `rec:`.
"""
    return text.strip('\n') + '\n'


if __name__ == '__main__':
    args = parse_args()
    if args.action == 'usage':
        print(usage())
        quit()
    elif args.action == 'test':
        import doctest
        doctest.testmod()
    elif args.action == 'do':
        for task in args.item:
            old_task = get_line(task)
            new_task = make_new_task(old_task)
            mark_done(task)
            if new_task:
                add_new_task(new_task)
