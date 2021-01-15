/**
 * @license
 * Copyright 2019 Fast Forward Labs.
 * Written by / Contact : https://github.com/victordibia
 * NeuralQA - NeuralQA: Question Answering on Large Datasets with BERT.
 * Licensed under the MIT License (the "License");
 * =============================================================================
 */

import React from "react";
import { NavLink } from "react-router-dom";
import "./header.css";

const Header = () => {
  const appName = "Data2Vis-Net";
  const appDescription = "Dataset for Automated Generation of Visualizations";
  return (
    <div>
      <div className="headermain" aria-label={appDescription}>
        <div className="  w-full  container-fluid   headerrow pl-1 ">
          <div className="flex  h-full">
            <div className="h-full   flex flex-col justify-center mr-2 ml-2  ">
              <a href={process.env.PUBLIC_URL + "/#"}>
                <img
                  className="headericon"
                  src="images/icon.png"
                  alt="NeuralQA logo"
                />
              </a>
            </div>
            <div className="apptitle  flex flex-col justify-center  mr-1">
              <div className="text-white  font-semibold text-sm  iblock mr-1">
                {" "}
                {appName}{" "}
              </div>
            </div>
            <div className="h-full   flex  text-sm  navbarlinks ">
              <NavLink exact to="/">
                Curation
              </NavLink>
            </div>
            {/* <div className="h100   flex flexjustifycenter  navbarlinks ">
              <NavLink exact to="/embeddings">
                Embeddings{" "}
              </NavLink>
            </div>
            <div className="h100   flex flexjustifycenter  navbarlinks ">
              <NavLink exact to="/livesearch">
                Live Search{" "}
              </NavLink>
            </div> */}
          </div>
        </div>
      </div>
      <div></div>
      <div className="headerboost"> </div>
    </div>
  );
};

export default Header;
