import "./main.css";

import { Route, HashRouter } from "react-router-dom";
import Footer from "./footer/Footer";
import Header from "./header/Header";

function Main() {
  return (
    <HashRouter>
      <div className="flex flex-col h-screen  ">
        <Header />
        <main className="container-fluid w-full   flex-grow p-2">
          ok
          {/* <Route
            exact
            path="/"
            render={(props) => <ModelViz {...props} selections={selections} />}
          /> */}
        </main>
        <Footer />
      </div>
    </HashRouter>
  );
}

export default Main;
