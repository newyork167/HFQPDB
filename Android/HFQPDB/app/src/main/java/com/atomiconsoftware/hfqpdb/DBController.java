package com.atomiconsoftware.hfqpdb;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;

/**
 * Created by newyork167 on 11/29/16.
 */

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Hashtable;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;

public class DBController extends SQLiteOpenHelper {

    private static DBController mInstance = null;
    private static Context context;

    public static final String DATABASE_NAME = "Library.db";
    public static final String BOOKS_TABLE_NAME = "books";
    public static final String BOOKS_COLUMN_ID = "id";
    public static final String BOOKS_COLUMN_TITLE = "title";
    public static final String BOOKS_COLUMN_AMAZON_URL = "amazon_url";
    public static final String BOOKS_COLUMN_DESCRIPTION = "description";
    public static final String BOOKS_COLUMN_LOCATION = "location";
    public static final String BOOKS_COLUMN_LANGUAGE = "language";
    public static final String BOOKS_COLUMN_DEWEY_NORMAL = "dewey_normal";
    public static final String BOOKS_COLUMN_AUTHOR = "author";
    public static final String BOOKS_COLUMN_EDITION_INFO = "edition_info";
    public static final String BOOKS_COLUMN_PHYSICAL_DESCRIPTION = "physical_description";
    public static final String BOOKS_COLUMN_IMAGE = "image";

    public static final String[] BOOKS_COLUMNS = new String[]{
            BOOKS_COLUMN_ID, BOOKS_COLUMN_TITLE, BOOKS_COLUMN_AMAZON_URL, BOOKS_COLUMN_DESCRIPTION, BOOKS_COLUMN_LOCATION,
            BOOKS_COLUMN_LANGUAGE, BOOKS_COLUMN_DEWEY_NORMAL, BOOKS_COLUMN_AUTHOR, BOOKS_COLUMN_EDITION_INFO,
            BOOKS_COLUMN_PHYSICAL_DESCRIPTION, BOOKS_COLUMN_IMAGE
    };

    public DBController(Context context) {
        super(context == null ? DBController.context : context, DATABASE_NAME , null, 1);
    }

    public static DBController getInstance(){
        if(mInstance == null)
        {
            mInstance = new DBController(context);
        }
        return mInstance;
    }

    public static void setContext(Context context) {
        DBController.context = context;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        // TODO Auto-generated method stub
        db.execSQL("CREATE TABLE IF NOT EXISTS books(id INT, " +
                "title VARCHAR, barcode VARCHAR, amazon_url VARCHAR, description VARCHAR, location VARCHAR," +
                "language VARCHAR, dewey_normal VARCHAR, author VARCHAR, edition_info VARCHAR, physical_description VARCHAR, image BLOB, tags VARCHAR);"
        );
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // TODO Auto-generated method stub
        db.execSQL("DROP TABLE IF EXISTS books");
        onCreate(db);
    }

    public boolean insertCoupon (Coupon coupon) {
        SQLiteDatabase db = this.getWritableDatabase();
//        db.execSQL("DROP TABLE IF EXISTS books;");
        db.execSQL("CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY, " +
                "title VARCHAR, barcode VARCHAR, amazon_url VARCHAR, description VARCHAR, location VARCHAR," +
                "language VARCHAR, dewey_normal VARCHAR, author VARCHAR, edition_info VARCHAR, physical_description VARCHAR, image BLOB, tags VARCHAR);"
        );

        int nextId = getNextID();

        ContentValues contentValues = new ContentValues();
        contentValues.put(BOOKS_COLUMN_TITLE, coupon.getTitle());

        try {
            Bitmap bmp = coupon.getCouponImage();
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            bmp.compress(Bitmap.CompressFormat.PNG, 100, stream);
            byte[] byteArray = stream.toByteArray();
            contentValues.put(BOOKS_COLUMN_IMAGE, byteArray);
        }
        catch (Exception ex){
            ex.printStackTrace();
        }

        try {
            db.insert(BOOKS_TABLE_NAME, null, contentValues);
        }
        catch (Exception ex){
            ex.printStackTrace();
        }
        return true;
    }

    public void deleteBook(int id){
        SQLiteDatabase db = this.getWritableDatabase();
        db.execSQL("DELETE FROM " + BOOKS_TABLE_NAME + " WHERE id = " + Integer.toString(id));
        Library.loadFromDB();
    }

    public boolean deleteAllBooks(){
        try {
            SQLiteDatabase db = this.getWritableDatabase();
            db.execSQL("DELETE FROM " + BOOKS_TABLE_NAME);
            Library.loadFromDB();
        }
        catch (Exception ex){
            return false;
        }

        return true;
    }

    public Cursor getData(int id) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor res =  db.rawQuery( "select * from books where id="+id+"", null );
        return res;
    }

    public int numberOfRows(){
        SQLiteDatabase db = this.getReadableDatabase();
        int numRows = (int) DatabaseUtils.queryNumEntries(db, BOOKS_TABLE_NAME);
        return numRows;
    }

    public ArrayList<Coupon> getAllCoupons() {
        ArrayList<Coupon> books = new ArrayList<>();

        try {
            //hp = new HashMap();
            SQLiteDatabase db = this.getReadableDatabase();
            Cursor res = db.rawQuery("select * from books", null);
            res.moveToFirst();

            while (!res.isAfterLast()) {
                Coupon book = new Coupon();
                book.setId(res.getInt(res.getColumnIndex(BOOKS_COLUMN_ID)));
                book.setTitle(res.getString(res.getColumnIndex(BOOKS_COLUMN_TITLE)));

                // Get image data
                try{
                    byte[] bitmapdata = res.getBlob(res.getColumnIndex(BOOKS_COLUMN_IMAGE));
                    Bitmap bitmap = BitmapFactory.decodeByteArray(bitmapdata, 0, bitmapdata.length);
                    book.setImage(bitmap);
                }
                catch (Exception ex){
                    Log.e("DBController", "Error getting image from database");
                }

                books.add(book);
                res.moveToNext();
            }

            res.close();
        }
        catch (Exception ex){
            ex.printStackTrace();
        }
        return books;
    }

    public int getNextID(){
        int nextID = -1;
        try {
            //hp = new HashMap();
            SQLiteDatabase db = this.getReadableDatabase();
            Cursor res = db.rawQuery("select max(id) from books", null);
            res.moveToFirst();

            while (!res.isAfterLast()) {
                nextID = res.getInt(0);
                res.moveToNext();
            }

            res.close();
        }
        catch (Exception ex){
            ex.printStackTrace();
        }

        return nextID;
    }
}
