import data.productcatalog.ProductTemplate;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.Base64;

class Main {
    public static void main(String[] args) throws Exception {
        // Foo originalObject = new Foo("str", 123);
        String injStr = args[0];
        ProductTemplate prodTempl = new ProductTemplate(injStr);
        String serializedObject = serialize(prodTempl);
        System.out.println("Serialized object: " + serializedObject);
        ProductTemplate deserializedObject = deserialize(serializedObject);
        System.out.println("Deserialized object ID: " + deserializedObject.getId());

        // Foo deserializedObject = deserialize(serializedObject);
        // System.out.println("Deserialized data str: " + deserializedObject.str + ", num: " + deserializedObject.num);
    }

    private static String serialize(Serializable obj) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream(512);
        try (ObjectOutputStream out = new ObjectOutputStream(baos)) {
            out.writeObject(obj);
        }
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }

    private static <T> T deserialize(String base64SerializedObj) throws Exception {
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(base64SerializedObj)))) {
            @SuppressWarnings("unchecked")
            T obj = (T) in.readObject();
            return obj;
        }
    }
}
