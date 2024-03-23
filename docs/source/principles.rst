Principles
==========

* Keep it simple, stupid.
* Queries are best done in an actual query language (e.g. SQL).
* Object hierarchies are not, and should not be, relations.
* Relations are not, and should not be, object hierarchies.
* Objects, however, can be useful for caching relational data and
  thereby reducing database load.
* Don't go after a fly with a sledgehammer.

Keep It Simple, Stupid
----------------------

I've tried to pare things down to the basics of what is most often needed while
getting data into and out of a relational database. Many of the more esoteric
lower-level things that can be done with a PEP 249 database module can't be done
directly in Abnormal. (Why should they? PEP 249 can do those just fine, and the
wrapped PEP 249 object is always available to be used.) At the same time,
however, I have also tried to provide easy ways to satisfy what I have found to
be the most common use cases. Keeping things simple means keeping them simple
for the user as well as the developer.

Queries Are Best Done in an Actual Query Language
-------------------------------------------------

A lot of very smart people at IBM spent a lot of time thinking about database
theory, relational operations, and how to let programmers express the latter
back in the 1970's. Anyone who thinks they can cook up something as good or
better in their spare time (usually something constrained by the syntax
limitations of a host language never intended for data retrieval) is probably
badly mistaken.

I feel very strongly about this, and 90% of ORM's lose (and lose badly) on this
account alone.

But it gets even worse: it turns out that generating efficient SQL is not
exactly easy. As a result, ORM's come with a performance cost. Abnormal is not
affected by this problem, by virtue of its queries being expressed in SQL.

Objects and Relations
---------------------

Objects have their place, and can be a useful tool to have in one's toolbox,
but too many developers treat object-oriented programming like the *only* tool
in their toolbox. If the only tool you are willing to use is a hammer, and
you treat the whole world like a nail, lossage is going to result.

The neat thing about relations is you don't have to think of everything ahead
of time. Need to know all parts on hand from all suppliers in London? ::

    curs = conn.cursor()
    query = """select p.pno as pno, p.pname as pname from sp
        join s on sp.sno = s.sno
        join p on sp.pno = p.pno
        where s.city = 'London'"""
    for result in curs.execute(query).into(mapping):
        print(result['pno'], result['pname'])


No need to go back and define a new SuppliersParts object (and all its assorted
relationships), or to pull in more data than you actually need, just because you
didn't think you would need this particular combination of data ahead of time.
A relational database simply generates novel row types on the fly, as needed.

Where Objects Can Be Useful
---------------------------

Theoretically, there is no need for objects at all. Just pass the primary
keys needed to retrieve the rows in question; instead of defining and passing
a User object, just pass a user ID. But if you do this, you will be querying
the database *a lot* for needed other bits of user information.

So the need to cache data arises, and in an object-oriented language like
Python, objects are a logical way to represent the cached data, and it would
be nice to have an easy way to get data into them.

Don't Go after a Fly with a Sledgehammer
----------------------------------------

In the name of making it easier to get data into and out of objects, and to
isolate the programmer from vendor-specific SQL, an entire object hierarchy, and
the relationships between those objects, must be defined. An entire new syntax
for retrieving data must be defined. What data one can retrieve is then
constrained by those pre-defined objects and their relationships.

Don't do all that. Just make it easier to get data into and out of Python
objects.
