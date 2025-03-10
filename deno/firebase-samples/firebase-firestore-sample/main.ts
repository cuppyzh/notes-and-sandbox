import {
  initializeApp,
} from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import {
addDoc,
  collection,
  getDocs,
  getFirestore,
  doc,
  setDoc,
  deleteDoc
} from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";
import {
  getAuth,
  signInWithEmailAndPassword,
} from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";
import { config } from "https://deno.land/x/dotenv/mod.ts";

// Load environment variables const env =
config();

// Firebase Setup
const firebaseConfig = JSON.parse(Deno.env.get("FIREBASE_APP_CONFIG") as string)
const firebaseApp = initializeApp(firebaseConfig, "hana-prod-api");
const auth = getAuth(firebaseApp);
const database = getFirestore(firebaseApp);

// Get authenticated
const email = Deno.env.get("FIREBASE_AUTH_EMAIL") as string;
const password = Deno.env.get("FIREBASE_AUTH_PASSWORD") as string;
const userCredential = await signInWithEmailAndPassword(
  auth,
  email,
  password,
);
console.log("User signed in: ", userCredential.user.email);

// Data specific configuration
const collectionName = "{collection-name}/"

const testCollection = collection(database, collectionName);

// Get Docs
const docs = await getDocs(testCollection);
const getData = docs.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
console.log("Data: \n" + JSON.stringify(getData))

// Add Docs with Defined Document ID
const documentId = "reference-id";
const docRef = doc(database, collectionName, documentId);
const data = { name: "John Doe", age: 30, email: "john.doe@example.com", };
await setDoc(docRef, data);

// Delete
await deleteDoc()