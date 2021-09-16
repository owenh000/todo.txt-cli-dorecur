=======
dorecur
=======

*dorecur* is an add-on for the `todo.txt-cli
<https://github.com/todotxt/todo.txt-cli/>`_ task manager that
provides a drop-in replacement for the *do* action. It handles
recurring tasks by adding a new task when the old task is finished. It
does not require an external scheduler such as cron.

-------------------------------
Keys (tags) used by this action
-------------------------------

- The ``rec:`` value specifies how the task recurs.

- The ``t:`` start (deferral/threshold) date, if it exists, is
  incremented as specified by the `rec:` value.

- The ``due:`` date, if it exists, is incremented as specified by the
  ``rec:`` value.

----------------
Recurrence types
----------------

*dorecur* supports two different recurrence types.

- *Normal recurrence* is suitable for a task that recurs based on the
  date of completion, such as "water the flowers".

- *Strict recurrence* is suitable for a task that recurs based on the
  start date and/or due date specified in the task, such as "pay
  rent".

------------------------
Recurrence specification
------------------------

The ``rec:`` value follows the format ``(+)X(d|b|w|m|y)``.

- Normal recurrence is indicated by omitting the ``+`` prefix. Include
  the ``+`` prefix to specify strict recurrence.

- ``X`` is an integer representing the magnitude of adjustment.

- An optional suffix indicates the time unit: days, business days,
  weeks, months, or years, respectively. The default is "days" if the
  suffix is omitted. Business day calculations ignore holidays. Month
  calculations simply increment the month and subtract days if
  necessary (see the last example in `Behavior`_, below).

--------
Behavior
--------

This section describes *dorecur's* exact behavior, with examples (and
abbreviated todo-txt output).

- No ``rec:`` key: the task is marked as completed and no new task is
  created. (The built-in todo-txt *do* action is executed directly.)

  .. code:: console

     $ todo-txt ls
     1 Fix lamp
     $ todo-txt do 1
     (No new task)

- No start date or due date: a new task is created with no changes.

  .. code:: console

     $ todo-txt ls
     1 Meet friend for tea rec:1
     $ todo-txt do 1
     1 Meet friend for tea rec:1

- A start date or a due date but not both: the adjustment is applied
  to the date given.

  .. code:: console

     $ todo-txt ls
     1 Water flowers t:2021-01-01 rec:5d
     $ date -I && todo-txt do 1
     2021-01-02
     1 Water flowers t:2021-01-07 rec:5d

     $ todo-txt ls
     1 Send birthday greeting to friend t:2021-04-04 rec:+1y
     $ todo-txt do 1
     1 Send birthday greeting to friend t:2022-04-04 rec:+1y

- Both start date and due date with *strict recurrence*: the
  adjustment is applied to both dates individually.

  .. code:: console

     $ todo-txt ls
     1 Pay rent t:2021-01-28 due:2021-02-01 rec:+1m
     $ todo-txt do 1
     1 Pay rent t:2021-02-28 due:2021-03-01 rec:+1m

- Both start date and due date with *normal recurrence*: the
  adjustment is applied to the start date only. The due date is
  adjusted by applying the offset between the start date and due date
  of the original task (as number of days).

  .. code:: console

     $ todo-txt ls
     1 Do offline backup t:2021-01-01 due:2021-01-08 rec:2w
     $ date -I && todo-txt do 1
     2021-01-03
     1 Do offline backup t:2021-01-17 due:2021-01-24 rec:2w

- A start or due date near the end of the month with a month unit for
  recurrence: a day-of-month greater than 28 may migrate backward
  toward the 28th.

  .. code:: console

     $ todo-txt ls
     1 Get groceries t:2021-01-14 rec:1m
     $ date -I && todo-txt do 1
     2021-01-31
     1 Get groceries t:2021-02-28 rec:1m

     $ todo-txt ls
     1 Pay rent t:2021-01-31 due:2021-02-01 rec:+1m
     $ todo-txt do 1
     1 Pay rent t:2021-02-28 due:2021-03-01 rec:+1m

----------
Installing
----------

The *dorecur* add-on can be installed by saving the ``dorecur.py``
file in your todo.txt-cli actions directory (``~/.todo.actions.d/``,
by default) and renaming it to ``do``.

Alternatively, clone the repository and create a symbolic link as
described below. (Replace ``~/repos`` with your preferred location.)
Note this **warning**, however: todo.txt-cli will ignore a broken
symbolic link. Therefore if the repository is moved in the future, you
will be marking recurring tasks as complete without creating new
ones. If this is a concern, simply copy the script into place and
rename as described above. (See `todo.txt-cli issue #359
<https://github.com/todotxt/todo.txt-cli/issues/359>`_.)

1. Clone the repository.

   .. code:: console

      $ cd ~/repos/
      $ git clone "https://github.com/owenh000/todo.txt-cli-dorecur.git"

2. Change to the todo.txt-cli actions directory
   (``~/.todo.actions.d``, by default). Then create a symbolic link to
   ``dorecur.py`` named ``do`` (the ``--relative`` option could be
   added to make the link more robust if the repository path is nearer
   the actions directory than the filesystem root).

   .. code:: console

      $ cd ~/.todo.actions.d
      $ ln --symbolic ~/repos/todo.txt-cli-dorecur/dorecur.py do

3. Future updates only require running ``git pull`` from inside the
   repository.

   .. code:: console

      $ cd ~/repos/todo.txt-cli-dorecur/
      $ git pull

-----------
Development
-----------

To run tests: ``./do-recur.py test``

-------
Credits
-------

This add-on is inspired by:

- `todo.txt-cli <https://github.com/todotxt/todo.txt-cli>`_, for which
  *dorecur* is an add-on

- The `again <https://github.com/nthorne/todo.txt-cli-again-addon>`_
  add-on, which was written in Bash and has a slightly different
  feature set

- The recurrence system of the `topydo
  <https://github.com/topydo/topydo>`_ task manager (though the
  recurrence behavior of *dorecur* is not identical)

------------
Contributing
------------

If you would like to contribute:

- Share this project with someone else who may be interested
- Contribute a fix for a currently open
  `issue <https://github.com/owenh000/todo.txt-cli-dorecur/issues>`_ (if
  any) using a GitHub pull request (please discuss before working on
  any large changes)
- Open a new issue for a problem you've discovered or a possible
  enhancement
- Sponsor my work through `GitHub Sponsors
  <https://github.com/owenh000>`_ (see also `owenh.net/support
  <https://owenh.net/support>`_)

---------------------
Copyright and License
---------------------

Copyright 2021 Owen T. Heisler. GNU General Public License v3 (GPLv3).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
