package com.atomiconsoftware.hfqpdb;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.Serializable;

/**
 * Created by newyork167 on 12/6/16.
 */

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;

public class BitmapDataObject implements Serializable {

    private Bitmap currentImage;

    public BitmapDataObject(Bitmap bitmap)
    {
        currentImage = bitmap;
    }

    private void writeObject(java.io.ObjectOutputStream out) throws IOException {

        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        currentImage.compress(Bitmap.CompressFormat.PNG, 100, stream);

        byte[] byteArray = stream.toByteArray();

        out.writeInt(byteArray.length);
        out.write(byteArray);

        currentImage = BitmapFactory.decodeByteArray(byteArray, 0, byteArray.length);

    }

    private void readObject(java.io.ObjectInputStream in) throws IOException, ClassNotFoundException {


        int bufferLength = in.readInt();

        byte[] byteArray = new byte[bufferLength];

        int pos = 0;
        do {
            int read = in.read(byteArray, pos, bufferLength - pos);

            if (read != -1) {
                pos += read;
            } else {
                break;
            }

        } while (pos < bufferLength);

        currentImage = BitmapFactory.decodeByteArray(byteArray, 0, bufferLength);
    }

    public Bitmap getImage(){
        return currentImage;
    }

    public void setImage(Bitmap image){
        this.currentImage = image;
    }
}