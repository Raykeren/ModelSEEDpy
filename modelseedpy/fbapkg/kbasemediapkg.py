# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from optlang.symbolics import Zero, add
from modelseedpy.fbapkg.basefbapkg import BaseFBAPkg
from modelseedpy.core.fbahelper import FBAHelper

#Base class for FBA packages
class KBaseMediaPkg(BaseFBAPkg):
    def __init__(self,model):
        BaseFBAPkg.__init__(self,model,"kbase media",{},{})

    def build_package(self,media_or_parameters,default_uptake = None,default_excretion = None):
        if isinstance(media_or_parameters,dict):
            self.validate_parameters(media_or_parameters,[],{
                "default_uptake":0,
                "default_excretion":100,
                "media":None
            })
        else:
            self.validate_parameters({},[],{
                "default_uptake":default_uptake,
                "default_excretion":default_excretion,
                "media":media_or_parameters
            })
            if self.parameters["default_uptake"] == None:
                self.parameters["default_uptake"] = 0
            if self.parameters["default_excretion"] == None:
                self.parameters["default_excretion"] = 100    
        if self.parameters["media"] == None:
            self.parameters["default_uptake"] = 100
        exchange_reactions = {}
        for reaction in self.model.reactions:
            if reaction.id[0:3].lower() == "ex_":
                compound = reaction.id[3:]
                exchange_reactions[compound] = reaction                
                reaction.lower_bound = -1*self.parameters["default_uptake"]
                reaction.upper_bound = self.parameters["default_excretion"]
                reaction.update_variable_bounds()
        if self.parameters["media"] != None:
            #Searching for media compounds in model
            for compound in self.parameters["media"].mediacompounds:
                mdlcpds = self.find_model_compounds(compound.id)
                for mdlcpd in mdlcpds:
                    if mdlcpd.id in exchange_reactions:
                        exchange_reactions[mdlcpd.id].lower_bound = -1 * compound.maxFlux
                        exchange_reactions[mdlcpd.id].upper_bound = -1 * compound.minFlux
                    if self.pkgmgr != None and "FullThermoPkg" in self.pkgmgr.packages:
                        if mdlcpd.id in self.variables["logconc"] and mdlcpd.compartment == "e0":
                            if compound.concentration != 0.001:
                                self.variables["logconc"][msid_hash[compound.id].id].lb = compound.concentration
                                self.variables["logconc"][msid_hash[compound.id].id].ub = compound.concentration
    
    def find_model_compounds(self,cpdid):
        if cpdid in self.model.metabolites:
            return [self.model.metabolites.get_by_id(cpdid)]
        mdlcpds = []
        for metabolite in self.model.metabolites:
            if FBAHelper.modelseed_id_from_cobra_metabolite(metabolite) == cpdid:
                mdlcpds.append(metabolite)
        return mdlcpds