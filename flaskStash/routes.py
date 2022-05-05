from flask import render_template, url_for, flash, redirect, request
from flaskStash.forms import RegistrationForm, LoginForm, SearchForm, UpdateProfileForm, AddToDatabase, AddToStashForm, AddToWishlist
from flaskStash.database import Users, Genres, Subgenres, Artists, Albums, Tracklists, User_Wishlists, User_Catalogs, Catalog_Genres, Formats 
from flaskStash import app, db, bcrypt, engine, func, my_session, text, func
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
import time


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage', page=1))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('homepage', page=1))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('Login.html', title='Mu Stash || Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage', page=1))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        month=str(form.birthMonth.data).split('-')[1]
        year=str(form.birthMonth.data).split('-')[0]
        user=Users(username=form.username.data, password=hashed_password, birth_month=month, birth_year=year)
        db.session.add(user)
        db.session.commit()
        flash(f'User created for {form.username.data}. Please login', 'success')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Mu Stash || Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_stash/<format_id>', methods=['GET', 'POST'])
def add_stash(format_id):
    form=AddToStashForm()
    album_info=db.engine.execute(text(f"SELECT artists.name, albums.name, albums.image_file, albums.id, formats.name FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON formats.album_id=albums.id WHERE formats.id={format_id}"))
    album_info=[row for row in album_info][0] 

    if form.validate_on_submit():
        if User_Catalogs.query.filter(User_Catalogs.album_id==album_info[3], User_Catalogs.user_id==current_user.id, User_Catalogs.format==int(format_id)).first() == None:
            print('user catalog')
            catalog=User_Catalogs(album_id=album_info[3], user_id=current_user.id, format=format_id, package_condition=form.package_condition.data, media_condition=form.media_condition.data, approx_resale_value=form.approx_resale_value.data, overall_rating=form.overall_rating.data, production_rating=form.production_rating.data, musicianship_rating=form.musicianship_rating.data, songwriting_rating=form.songwriting_rating.data, vocals_rating=form.vocals_rating.data,  lyrics_rating=form.lyrics_rating.data)
            db.session.add(catalog)
            db.session.commit()
        time.sleep(.01)
        if Genres.query.filter(Genres.name==form.genre.data).first()==None:
            print('genre')
            genre = Genres(name=form.genre.data)
            db.session.add(genre)
            db.session.commit()
        time.sleep(.01)  
        if Subgenres.query.filter(Subgenres.name==form.subgenre.data, Subgenres.genre_id==(Genres.query.filter(Genres.name==form.genre.data).first()).id).first() == None:
            print('subgenre')
            subgenre = Subgenres(name=form.subgenre.data, genre_id=(Genres.query.filter(Genres.name==form.genre.data).first()).id )
            db.session.add(subgenre)
            db.session.commit() 
        time.sleep(.01)
        if Catalog_Genres.query.filter(Catalog_Genres.genre_id==(Genres.query.filter(Genres.name==form.genre.data).first()).id, Catalog_Genres.subgenre_id==((Subgenres.query.filter(Subgenres.name==form.subgenre.data, Subgenres.genre_id==((Genres.query.filter(Genres.name==form.genre.data)).first()).id)).first()).id, Catalog_Genres.user_catalog_id==((User_Catalogs.query.filter(User_Catalogs.album_id==album_info[3], User_Catalogs.user_id==current_user.id, User_Catalogs.format==format_id)).first()).id).first() == None:
            print('cg')
            catalog_genre = Catalog_Genres(genre_id=(Genres.query.filter(Genres.name==form.genre.data).first()).id, subgenre_id=((Subgenres.query.filter(Subgenres.name==form.subgenre.data, Subgenres.genre_id==((Genres.query.filter(Genres.name==form.genre.data)).first()).id)).first()).id, user_catalog_id=((User_Catalogs.query.filter(User_Catalogs.album_id==album_info[3], User_Catalogs.user_id==current_user.id, User_Catalogs.format==format_id)).first()).id)
            db.session.add(catalog_genre)
            db.session.commit()

        album_info=db.engine.execute(text(f"SELECT artists.name, albums.name, albums.image_file, albums.id, formats.name, formats.id FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON formats.album_id=albums.id WHERE formats.id={format_id}"))
        album_info=[row for row in album_info][0] 
        if User_Wishlists.query.filter(User_Wishlists.user_id==current_user.id, User_Wishlists.album_id==album_info[3], User_Wishlists.format==album_info[5]).first():
            wishlist_item=(User_Wishlists.query.filter(User_Wishlists.user_id==current_user.id, User_Wishlists.album_id==album_info[3], User_Wishlists.format==album_info[5]).first()).id
            wishlist_item=User_Wishlists.query.filter_by(id=wishlist_item)
            wishlist_item.delete()
            db.session.commit()

        return redirect(url_for('stash', page=1))

        # catalog_id=(User_Catalogs.query.filter(User_Catalogs.album_id==album_info[7], User_Catalogs.user_id==current_user.id, User_Catalogs.format==format_id,).first()).id

    return render_template('addToStash.html', title='Mu Stash || Add To Stash', form=form, format_id=format_id, album_info=album_info, current_user=current_user)

@app.route('/add_wishlist/<int:format_id>', methods=['GET', 'POST'])
def add_wishlist(format_id):
    album_info=db.engine.execute(text(f"SELECT artists.name, albums.name, albums.image_file, albums.id, formats.name, formats.id FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON formats.album_id=albums.id WHERE formats.id={format_id}"))
    album_info=[row for row in album_info][0] 
    album_ratings=db.engine.execute(text(f'SELECT AVG(user__catalogs.overall_rating), AVG(user__catalogs.production_rating), AVG(user__catalogs.musicianship_rating), AVG(user__catalogs.songwriting_rating), AVG(user__catalogs.vocals_rating), AVG(user__catalogs.lyrics_rating) FROM user__catalogs WHERE user__catalogs.format={album_info[5]}')).first()
    form=AddToWishlist()
    if form.validate_on_submit():
        if User_Wishlists.query.filter(User_Wishlists.user_id==current_user.id, User_Wishlists.album_id==album_info[3], User_Wishlists.format==album_info[5]).first() == None:
            wishlist_item=User_Wishlists(user_id=current_user.id, album_id=album_info[3], format=album_info[5], purchase_priority=int((form.purchase_priority.data.split(' ')[0])))
            db.session.add(wishlist_item)
            db.session.commit()
            return redirect(url_for('wishlist', page=1))
    return render_template('addToWishlist.html', title='Mu Stash || Add To Stash', format_id=format_id, album_info=album_info, form=form, album_ratings=album_ratings)

@app.route('/remove_stash/<int:format_id>', methods=['GET', 'POST'])
def remove_stash(format_id):
    if User_Catalogs.query.filter(User_Catalogs.format==format_id, User_Catalogs.user_id==current_user.id):
        catalog_item=(User_Catalogs.query.filter(User_Catalogs.format==format_id, User_Catalogs.user_id==current_user.id)[0]).id
        catalog_item=User_Catalogs.query.filter_by(id=catalog_item)
        catalog_item.delete()
        db.session.commit()
    return redirect(url_for('stash', page=1))


@app.route('/remove_wishlist/<int:format_id>', methods=['GET', 'POST'])
def remove_wishlist(format_id):
    if User_Wishlists.query.filter(User_Wishlists.format==format_id, User_Wishlists.user_id==current_user.id):
        wishlist_item=(User_Wishlists.query.filter(User_Wishlists.format==format_id, User_Wishlists.user_id==current_user.id)[0]).id
        wishlist_item=User_Wishlists.query.filter_by(id=wishlist_item)
        wishlist_item.delete()
        db.session.commit()
    return redirect(url_for('wishlist', page=1))



@app.route('/homepage/<int:page>', methods=['GET', 'POST'])
@login_required
def homepage(page):
    page=int(page)
    # page=request.args.get('page', 1, type=int)
    form=SearchForm()
    album_basic_results=db.engine.execute(text(f"SELECT albums.id, albums.name, albums.year, albums.image_file, artists.name, formats.name, formats.id FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON albums.id=formats.album_id ORDER BY artists.name ASC"))
    album_basic_results=[row for row in album_basic_results]
    album_ratings=db.engine.execute(text(f"SELECT albums.id, user__catalogs.id, user__catalogs.format, user__catalogs.user_id, user__catalogs.overall_rating FROM albums INNER JOIN user__catalogs ON user__catalogs.album_id=albums.id WHERE user__catalogs.user_id = {current_user.id}"))
    album_ratings=[row for row in album_ratings]
    album_wishlist=db.engine.execute(text(f"SELECT albums.id, user__wishlists.id, user__wishlists.format, user__wishlists.user_id FROM albums INNER JOIN user__wishlists ON user__wishlists.album_id=albums.id WHERE user__wishlists.user_id = {current_user.id}"))
    album_wishlist=[row for row in album_wishlist]
    rating=db.session.query(func.avg(User_Catalogs.overall_rating), func.count(User_Catalogs.overall_rating))
    stash=User_Catalogs.query
    wishlist=User_Wishlists.query
    # stash=db.engine.execute(text("SELECT user__catalogs.album_id, user__catalogs.user_id FROM user__catalogs JOIN formats ON user__catalogs.format=formats.id GROUP BY user__catalogs.album_id ORDER BY user__catalogs.album_id ASC"))
    if form.validate_on_submit:
        if form.searched.data:
            print('here')
            return redirect(url_for('search', page=1, query=form.searched.data))

    return render_template('Homepage.html', title='Mu Stach || Homepage', form=form, page=page, album_basic_results=album_basic_results, album_ratings=album_ratings, album_wishlist=album_wishlist, db=db, text=text, current_user=current_user, rating=rating, User_Catalogs=User_Catalogs, User_Wishlists=User_Wishlists, stash=stash, wishlist=wishlist, len=len(album_basic_results), source='homepage')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = UpdateProfileForm()
    month_list=['January', "Febuary", 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month = month_list[current_user.birth_month - 1]
    catalog=User_Catalogs
    wishlist=User_Wishlists
    stash_query=db.engine.execute(text(f"SELECT SUM(approx_resale_value) FROM user__catalogs WHERE user_id={current_user.id}")).first()[0]
    if stash_query == 'None':
        stash_value='0'
    else:
        stash_value= stash_query
    stash_length=catalog.query.filter_by(user_id=current_user.id).count()
    wishlist_length=len(wishlist.query.filter_by(user_id=current_user.id).all())
    if form.validate_on_submit():
        month=str(form.birthMonth.data).split('-')[1]
        year=str(form.birthMonth.data).split('-')[0]
        current_user.username=form.username.data
        current_user.birth_month=month
        current_user.birth_year=year
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method=='GET':
        form.username.data=current_user.username
    return render_template('profile.html', title='Mu Stach || Profile', form=form,  month=month, wishlist_length=wishlist_length, stash_length=stash_length, stash_value=stash_value)

@app.route('/stash/<int:page>')
@login_required
def stash(page):
    page=int(page)
    # page=request.args.get('page', 1, type=int)
    form=SearchForm()
    album_basic_results=db.engine.execute(text(f"SELECT albums.id, albums.name, albums.year, albums.image_file, artists.name, formats.name, formats.id FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON albums.id=formats.album_id INNER JOIN user__catalogs ON user__catalogs.format=formats.id WHERE user__catalogs.user_id={current_user.id} ORDER BY artists.name ASC"))
    album_basic_results=[row for row in album_basic_results]
    album_ratings=db.engine.execute(text("SELECT albums.id, user__catalogs.id, user__catalogs.format, user__catalogs.user_id, user__catalogs.overall_rating FROM albums INNER JOIN user__catalogs ON user__catalogs.album_id=albums.id"))
    album_ratings=[row for row in album_ratings]
    album_wishlist=db.engine.execute(text("SELECT albums.id, user__wishlists.id, user__wishlists.format, user__wishlists.user_id FROM albums INNER JOIN user__wishlists ON user__wishlists.album_id=albums.id"))
    album_wishlist=[row for row in album_wishlist]
    rating=db.session.query(func.avg(User_Catalogs.overall_rating), func.count(User_Catalogs.overall_rating))
    stash=User_Catalogs.query
    wishlist=User_Wishlists.query
    # stash=db.engine.execute(text("SELECT user__catalogs.album_id, user__catalogs.user_id FROM user__catalogs JOIN formats ON user__catalogs.format=formats.id GROUP BY user__catalogs.album_id ORDER BY user__catalogs.album_id ASC"))
    if form.validate_on_submit:
        if form.searched.data:
            print('here')
            return redirect(url_for('search', page=1, query=form.searched.data))


    return render_template('stash.html', title='Mu Stach || My Stash', form=form, page=page, album_basic_results=album_basic_results, album_ratings=album_ratings, album_wishlist=album_wishlist, db=db, text=text, current_user=current_user, rating=rating, User_Catalogs=User_Catalogs, User_Wishlists=User_Wishlists, stash=stash, wishlist=wishlist, len=len(album_basic_results), source='stash'  )


@app.route('/wishlist/<int:page>')
@login_required
def wishlist(page):
    page=int(page)
    # page=request.args.get('page', 1, type=int)
    form=SearchForm()
    album_basic_results=db.engine.execute(text(f"SELECT albums.id, albums.name, albums.year, albums.image_file, artists.name, formats.name, formats.id FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON albums.id=formats.album_id INNER JOIN user__wishlists ON user__wishlists.format=formats.id WHERE user__wishlists.user_id={current_user.id} ORDER BY user__wishlists.purchase_priority DESC"))
    album_basic_results=[row for row in album_basic_results]
    album_ratings=db.engine.execute(text("SELECT albums.id, user__catalogs.id, user__catalogs.format, user__catalogs.user_id, user__catalogs.overall_rating FROM albums INNER JOIN user__catalogs ON user__catalogs.album_id=albums.id"))
    album_ratings=[row for row in album_ratings]
    album_wishlist=db.engine.execute(text("SELECT albums.id, user__wishlists.id, user__wishlists.format, user__wishlists.user_id FROM albums INNER JOIN user__wishlists ON user__wishlists.album_id=albums.id"))
    album_wishlist=[row for row in album_wishlist]
    rating=db.session.query(func.avg(User_Catalogs.overall_rating), func.count(User_Catalogs.overall_rating))
    stash=User_Catalogs.query
    wishlist=User_Wishlists.query
    # stash=db.engine.execute(text("SELECT user__catalogs.album_id, user__catalogs.user_id FROM user__catalogs JOIN formats ON user__catalogs.format=formats.id GROUP BY user__catalogs.album_id ORDER BY user__catalogs.album_id ASC"))

    if form.validate_on_submit:
        if form.searched.data:
            print('here')
            return redirect(url_for('search', page=1, query=form.searched.data))

    return render_template('wishlist.html', title='Mu Stach || My Wishlist', form=form, page=page, album_basic_results=album_basic_results, album_ratings=album_ratings, album_wishlist=album_wishlist, db=db, text=text, current_user=current_user, rating=rating, User_Catalogs=User_Catalogs, User_Wishlists=User_Wishlists, stash=stash, wishlist=wishlist, len=len(album_basic_results), source='wishlist' )

def addArt(form_picture):
    rand_hex=secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn=rand_hex + f_ext
    picture_path=os.path.join(app.root_path, 'static/AlbumArt', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/add-to-database', methods=['GET', 'POST'])
@login_required
def addToDatabase():
    form=AddToDatabase()
    picture_file='static/AlbumArt/default.jpg'
    if form.validate_on_submit():
        if  form.image_file.data:
            picture_file=addArt(form.image_file.data)
        if (Artists.query.filter_by(name=form.artist.data).first()) == None:
            new_artist=Artists(name=form.artist.data)
            db.session.add(new_artist)
            db.session.commit()
        if (Albums.query.filter_by(name=form.album.data, artist_id=(Artists.query.filter_by(name=form.artist.data).first()).id ).first()) == None:
        # if (Albums.query.filter(name=form.album.data, artist_id=(Artists.query.filter_by(name=form.artist.data).first()).id ).first()) == None:
            time.sleep(.01)
            new_album=Albums(artist_id=(Artists.query.filter_by(name=form.artist.data).first()).id, image_file=picture_file, name=form.album.data, year=form.year.data)
            db.session.add(new_album)
            db.session.commit()
        time.sleep(.01)
        if (Formats.query.filter_by(name=form.format.data, album_id=(Albums.query.filter_by(name=form.album.data, artist_id=(Artists.query.filter_by(name=form.artist.data).first()).id ).first()).id).first()) == None:
            print(form.format.data)
            time.sleep(.01)
            new_format=Formats(album_id=(Albums.query.filter_by(name=form.album.data, artist_id=(Artists.query.filter_by(name=form.artist.data).first()).id ).first()).id, name=form.format.data)
            db.session.add(new_format)
            db.session.commit()
        return redirect(url_for('homepage', page=1))
    # image_file=  url_for('static', filename='AlbumArt/' + Albums.query.first().image_file)
    return render_template('addToDatabase.html', title='Mu Stach || Add To Database', form=form, picture_file=picture_file)


@app.route('/album/<string:album_name>/<int:format_id>')
@login_required
def album(album_name, format_id):
    album_name=album_name
    format_id=format_id
    return render_template('album.html', title='Mu Stach || Album')

@app.route('/search/<int:page>/<string:query>', methods=['GET', 'POST'])
def search(page, query):
    page=int(page)
    query=str(query)
    form=SearchForm()
    album_basic_results=db.engine.execute(text(f"SELECT albums.id, albums.name, albums.year, albums.image_file, artists.name, formats.name, formats.id FROM artists INNER JOIN albums ON albums.artist_id=artists.id INNER JOIN formats ON albums.id=formats.album_id INNER JOIN user__catalogs ON user__catalogs.format=formats.id INNER JOIN catalog__genres ON catalog__genres.user_catalog_id=user__catalogs.id WHERE artists.name LIKE '%{query}%' OR albums.name LIKE '%{query}%' OR formats.name LIKE '%{query}%'"))
    album_basic_results=[row for row in album_basic_results]
    #  OR catalog__genres.subgenre_id=id IN (SELECT subgenres.id FROM subgenres WHERE name LIKE '%{query}%') OR catalog__genres.genre_id=id IN(SELECT genres.id FROM genres WHERE name LIKE '%{query}%') 
    album_ratings=db.engine.execute(text("SELECT albums.id, user__catalogs.id, user__catalogs.format, user__catalogs.user_id, user__catalogs.overall_rating FROM albums INNER JOIN user__catalogs ON user__catalogs.album_id=albums.id"))
    album_ratings=[row for row in album_ratings]
    album_wishlist=db.engine.execute(text("SELECT albums.id, user__wishlists.id, user__wishlists.format, user__wishlists.user_id FROM albums INNER JOIN user__wishlists ON user__wishlists.album_id=albums.id"))
    album_wishlist=[row for row in album_wishlist]
    rating=db.session.query(func.avg(User_Catalogs.overall_rating), func.count(User_Catalogs.overall_rating))
    stash=User_Catalogs.query
    wishlist=User_Wishlists.query
    # stash=db.engine.execute(text("SELECT user__catalogs.album_id, user__catalogs.user_id FROM user__catalogs JOIN formats ON user__catalogs.format=formats.id GROUP BY user__catalogs.album_id ORDER BY user__catalogs.album_id ASC"))

    if form.validate_on_submit:
        if form.searched.data:
            print('here')
            return redirect(url_for('search', page=1, query=form.searched.data))

    return render_template('searchResults.html', title='Mu Stach || Search Results', form=form, page=page, query=query, album_basic_results=album_basic_results, album_ratings=album_ratings, album_wishlist=album_wishlist, db=db, text=text, current_user=current_user, rating=rating, User_Catalogs=User_Catalogs, User_Wishlists=User_Wishlists, stash=stash, wishlist=wishlist, len=len(album_basic_results), source='wishlist' )

   

def getAlbums():
    album_basic_results=db.engine.execute(text("SELECT albums.id, albums.name, albums.year, albums.image_file, artists.name FROM artists INNER JOIN albums ON albums.artist_id=artists.id"))
    
    print(album_basic_results)
    # print(album_basic_results.first())
    # print(album_basic_results.first()[0])
    # print(album_basic_results.first()[0][3])
    names=[row for row in album_basic_results]
    print(names[0][1])
    
    album_ratings=db.engine.execute(text("SELECT albums.id, user__catalogs.id, user__catalogs.format, user__catalogs.user_id, user__catalogs.overall_rating FROM albums INNER JOIN user__catalogs ON user__catalogs.album_id=albums.id"))
   
    print(album_ratings)
    names=[row for row in album_ratings]
    print(names)

    album_wishlist=db.engine.execute(text("SELECT albums.id, user__wishlists.id, user__wishlists.format, user__wishlists.user_id FROM albums INNER JOIN user__wishlists ON user__wishlists.album_id=albums.id"))
    
    print(album_wishlist)
    names=[row for row in album_wishlist]
    print(names)

    pass