# gnome-contacts vCard Importer

Imports version 2.1 vCards into the Gnome-Contacts contact database. I made this in order to import the contacts from my old phone so there could be some cases not handled (such as NICKNAME which came in vCard 3.0).

# Running

In order to run, you need the contacts.db from gnome-contacts. On my system, it was at the path `~/.local/share/evolution/addressbook/system/contacts.db`. Make sure you backup the file first just in case.

Once you have the contacts.db and your vCard file, you just need to pass them both as command line parameters.

Example:

```bash
./contactimporter.py contacts.db Contacts.vcf
```

The program will print the full_name of every contact it inserts. Once it's done, open the gnome-contacts app and make sure everything loaded properly.
