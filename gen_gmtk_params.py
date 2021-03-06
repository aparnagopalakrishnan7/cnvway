from collections import OrderedDict

MC_TYPE_DIAG = "COMPONENT_TYPE_DIAG_GAUSSIAN"
MC_TYPE_GAMMA = "COMPONENT_TYPE_GAMMA"
MC_TYPE_MISSING = "COMPONENT_TYPE_MISSING_FEATURE_SCALED_DIAG_GAUSSIAN"
COPY_PARENT = "internal:copyParent"


def generate_gmtk_obj_names(obj, track_names, num_segs, num_subsegs,
                            distribution, num_mix_components):
    """
    Generate GMTK object names for the types:
    NameCollection: "col"
    entries in NameCollection: "mx_name"
    Covar: "covar", "tied_covar"
    Mean: "mean"
    MX: "mx"
    MC: "mc_diag", "mc_gamma", "mc_missing", "gammascale"
    DPMF: "dpmf"
    :param obj: str: type of gmtk object for which names must be generated
    :param: track_names: list[str]: list of all track names
    :param: num_segs: int: number of segs
    :param: num_subsegs: int: number of subsegs
    :param: distribution: str: distribution
    :param: number of mixture components
    :return:
    """
    allowed_types = ["mx", "mc_diag", "mc_gamma", "mc_missing", "mean",
                     "covar", "col", "mx_name", "dpmf", "gammascale",
                     "gammashape", "tied_covar"]
    if not obj in allowed_types:
        raise ValueError("Undefined GMTK object type: {}".format(obj))

    names = []
    if obj == "covar":
        for name in track_names:
            names.append("covar_{}".format(name))

   
    # todo check component suffix
    elif obj == "tied_covar":
        for name in track_names:
            names.append("covar_{}".format(name))

    elif obj == "col":
        for name in track_names:
            names.append("collection_seg_{}".format(name))

    elif obj == "mx_name":
        for name in track_names:
            for i in range(num_segs):
                for j in range(num_subsegs):
                    line = "mx_seg{}_subseg{}_{}".format(i, j, name)
                    names.append(line)

    elif obj == "dpmf" and num_mix_components == 1:
        return ["dpmf_always"]

    else:
        for i in range(num_segs):
            for j in range(num_subsegs):
                for name in track_names:
                    # TODO check component suffix diff
                    if obj == "mc_diag":
                        line = "mc_{}_seg{}_subseg{}_{}".format(distribution,
                                                                i, j, name)
                    # TODO

                    # if obj == "mc_gamma":
                    # covered in general name generation
                    #     line = "{}_{}_seg{}_subseg{}_{}".format(obj,
                    #                         distribution, i, j, name)

                    # TODO
                    elif obj == "mc_missing":
                        line = ""

                    else:
                        line = "{}_seg{}_subseg{}_{}".format(obj, i, j, name)
                    names.append(line)

    return names

class DenseCPT:
    """
    A single DenseCPT object.
    Attributes:
    parent_card
    cardinality
    prob
    """
    def __init__(self, name, cardinality, prob, parent_card=-1):
        """
        name: str
        parent_card: str/int or list[str/int]
        cardinality: str/int
        prob: list[float]
        """
        self.name = name
        if parent_card != -1:
            if not isinstance(parent_card, list):
                self.parent_card = [parent_card]
            else:
                self.parent_card = parent_card
        else:
            self.parent_card = -1
        self.cardinality = cardinality
        # TODO array
        self.prob = prob

    def generate(self, index):
        """
        Returns string format of DenseCPT to be printed into input.master
        file (new lines to be added).
        index: int
        index of the denseCPT
        """
        lines = []
        line = []
        line.append(str(index))
        line.append(self.name)
        if self.parent_card == -1:  # no parents
            num_parents = 0
            parent_card_str = [""]
        else:
            num_parents = len(self.parent_card)
            parent_card_str = []
            for i in range(num_parents):
                parent_card_str.append(str(self.parent_card[i]))
        line.append(str(num_parents))
        if self.parent_card != -1:
            line.extend(parent_card_str)
        line.append(str(self.cardinality))
        lines.append(" ".join(line))
        lines.append(self.generate_prob(self.prob) + "\n")
        lines.append("\n")
        return "\n".join(lines)

    def generate_prob(self, prob):
        """
        Generates format of probabilities for single DenseCPT.
        :param prob: list[float]
        probabilities of DenseCPT
        :return: string format to be used by DenseCPT.generate()
        """
        line = []
        if isinstance(prob[0], float):
            prob_str = []
            for i in range(len(prob)):
                prob_str.append(str(prob[i]))
            return " ".join(prob_str)
        else:

            for i in range(len(prob)):
                line.append(self.generate_prob(prob[i]))
                # TODO check if it works without that one line gap
        return "\n".join(line)


class DeterministicCPT:
    """
    A single DeterministicCPT objects.
    Attributes:
        parent_card: str/int or list[str/int]
        cardinality: str/int
        name_of_existing_DT: str
    """

    def __init__(self, name, parent_card, cardinality, dt):
        """
        name: str
        parent_card: str/int or list[str/int]
        cardinality: str/int
        dt: str
        """
        self.name = name
        if not isinstance(parent_card, list):
            self.parent_card = [parent_card]
        else:
            self.parent_card = parent_card

        self.cardinality = cardinality
        self.dt = dt

    def generate(self, index):
        """
        :return: String format of DeterministicCPT to be printed into
        input.master
        file (new lines to be added).
        index: int
        index of DeterministicCPT
        """
        lines = []
        line = []
        line.append(str(index))
        line.append(self.name)
        lines.append(" ".join(line))
        lines.append(str(len(self.parent_card)))
        num_parents_cardinalities = []
        num_parents_cardinalities.extend(self.parent_card)
        num_parents_cardinalities.append(self.cardinality)
        lines.append(" ".join(num_parents_cardinalities))
        lines.append(self.dt)
        lines.append("\n")

        return "\n".join(lines)


class NameCollection:
    """
    A single NameCollection object.
    Attributes:
    names: list[str] or str
    """

    def __init__(self, name, *args):
        """
        name: str
        name of collection
        :param args: str
        name in name collection
        """
        self.name = name
        self.names_in_col = []
        for name in args:
            if isinstance(name, list):
                self.names_in_col.extend(name)
            else:
                self.names_in_col.append(name)

    def generate(self, index):
        """
        Returns string format of NameCollection objects to be printed into the
        input.master file (new lines to be added)
        index: int
        index of name collection
        """
        line = []
        line.append(str(index))
        line.append(self.name)
        line.append(str(len(self.names_in_col)))

        lines = []
        lines.append(" ".join(line))
        lines.append("\n".join(self.names_in_col))
        lines.append("\n")

        return "\n".join(lines)


class Mean:
    """
    A single Mean object.
    name: str
    value: list[float] or float
    Mean values of the Mean object.
    """

    def __init__(self, name, *args):
        """
        name: str
        name of mean object
        :param args: float
        mean values
        """
        self.name = name
        self.mean_values = []
        for val in args:
            self.mean_values.append(val)

    def generate(self, index):
        """
        Returns the string format of the Mean object to be printed into the
        input.master file (new lines to be added).
        index: int
        index of mean object
        :return:
        """
        line = []
        line.append(str(index))
        line.append(self.name)
        line.append(str(len(self.mean_values)))
        mean_str = []
        for i in self.mean_values:
            mean_str.append(str(i))
        line.extend(mean_str)
        line.append("\n")

        return " ".join(line)


class MC:
    """
    A single all MC objects.
    Value: list
    mc = MC()
    mc1 = [26, 0, "mean_0", "covar_0"]
    <mc_name>= [<dimensionality>, <type>, <mean of mc>, <covar of mc>]
    """
    def __init__(self, name, dim, type, mean=Mean('sample_mean'),
                 covar=Mean('sample_covar'), weights=[], gamma_shape="",
                 gamma_scale=""):
        """
        name: str
        name of MC object
        :param dim: str/int
        dimensionality of mc
        :param type: str/int
        type of mc
        :param mean: Mean
        mean of mc
        :param covar: Covar
        covar of mc
        """
        self.name = name
        self.mean = mean
        self.covar = covar
        self.dim = dim
        self.type = type
        # TODO
        self.weights = weights
        self.gamma_shape = gamma_shape
        self.gamma_scale = gamma_scale

    def generate(self, index):
        """
        Returns string format of MC object to be printed into the input.master
        file (new lines to be added).
        index: int
        index of mc object
        :return:
        """
        line = []
        line.append(str(index))
        line.append(str(self.dim))

        if self.type == MC_TYPE_GAMMA:
            # TODO min track
            line.append(str(self.type))
            line.append(self.gamma_scale)
            line.append(self.gamma_shape)

        elif self.type == MC_TYPE_MISSING:
            line.append(str(self.type))
            line.append(self.name)
            line.append(self.mean.name)
            line.append(self.covar.name)
            line.append("matrix_weightscale_1x1")
            line.append("\n")
        else: # default and for MC_TYPE_DIAG
            # TODO component_suffix
            line.append(str(self.type))
            line.append(self.name)
            line.append(self.mean.name)
            line.append(self.covar.name)
            line.append("\n")

        return " ".join(line)


class MX:
    """
    A single MX object.
    """
    def __init__(self, name, dim, dpmf, components):
        """
        name: str
        name of MX object
        dimensionality: int
        dpmf: DPMF
        components: list[mc] or mc (component)
        """
        self.name = name
        self.dim = dim
        if not isinstance(components, list):
            components  = [components]
        if len(dpmf.dpmf_values) != len(components):
            raise ValueError("Dimension of DPMF object must be equal " +
                             "to number of components of MX.")
        self.comp = components
        self.dpmf = dpmf

    def generate(self, index):
        """
        Returns string format of MX object to be printed into the input.master
        file (new lines to be added).
        index: int
        index of mx object
        :return:
        """
        line = []
        line.append(str(index))
        line.append(str(self.dim))
        line.append(self.name)
        line.append(str(len(self.comp)))  # num components
        line.append(self.dpmf.name)
        comp_names = []
        for comp in self.comp:
            comp_names.append(comp.name)
        line.extend(comp_names)
        line.append("\n")

        return " ".join(line)


class Covar:
    """
    A single Covar object.
    """

    def __init__(self, name, *args):
        """
        name: str
        name of MX object
        :param args: covar values
        """
        self.name = name
        self.covar_values = []
        for val in args:
            self.covar_values.append(val)

    def generate(self, index):
        """
        Returns string format of Covar object to be printed into the
        input.master
        file (new lines to be added).
        index: int
        index of Covar object
        :return:
        """
        line = []
        line.append(str(index))
        line.append(self.name)
        line.append(str(len(self.covar_values)))
        covar_str = []
        for i in self.covar_values:
            covar_str.append(str(i))
        line.extend(covar_str)
        line.append("\n")

        return " ".join(line)


class DPMF:
    """
    A single DPMF object.
    """

    def __init__(self, name, *args):
        """
        name: str
        name of dpmf object
        :param args: dpmf values summing to 1

        """
        self.name = name
        self.dpmf_values = []
        for val in args:
            self.dpmf_values.append(val)
        print("dpmf_val", self.dpmf_values)
        if sum(self.dpmf_values) != 1.0:
            self.dpmf_values = []
            raise ValueError("DPMF values must sum to 1.0.")

    def generate(self, index):
        """
         Returns string format of DPMF object to be printed into the
         input.master
        file (new lines to be added).
        :return:
        """
        line = []
        line.append(str(index))
        line.append(self.name)
        line.append(str(len(self.dpmf_values)))
        dpmf_str = []
        for i in self.dpmf_values:
            dpmf_str.append(str(i))
        line.extend(dpmf_str)
        line.append("\n")
        return " ".join(line)


class Object:

    def __new__(cls, _name, content, _kind):
        pass

    def __init__(self, name, content, kind):
        pass


class InputMaster:
    """
    Main class to produce the input.master file.
    Attributes:
        mean: OrderedDict
        covar: OrderedDict
        dense: OrderedDict
        deterministic: OrderedDict
        dpmf: OrderedDict
        mc: OrderedDict
        mx: OrderedDict
        name_collection: OrderedDict
        key: name of object
        value: GMTKObject instance
    """

    def __init__(self):
        self.mean = OrderedDict()
        self.covar = OrderedDict()
        self.dense = OrderedDict()
        self.deterministic = OrderedDict()
        self.dpmf = OrderedDict()
        self.mc = OrderedDict()
        self.mx = OrderedDict()
        self.name_collection = OrderedDict()

    def update(self, gmtk_obj):
        """
        gmtk_obj: list or single gmtk object
        List of GMTK objects
        """
        if not isinstance(gmtk_obj, list):
            gmtk_obj = [gmtk_obj]
        for obj in gmtk_obj:
            if not (isinstance(obj, Mean) or isinstance(obj, Covar) or
                    isinstance(obj, DeterministicCPT) or isinstance(obj,
                                                                    DenseCPT)
                    or isinstance(obj, DPMF) or isinstance(obj, MC)
                    or isinstance(obj, MX) or isinstance(obj, NameCollection)):

                raise ValueError("Object is not an allowed GMTK type.")

        for obj in gmtk_obj:  # all objects are of allowed types

            name = obj.name

            if isinstance(obj, Mean):
                self.mean[name] = obj
            if isinstance(obj, Covar):
                self.covar[name] = obj
            if isinstance(obj, DeterministicCPT):
                self.deterministic[name] = obj
            if isinstance(obj, DenseCPT):
                self.dense[name] = obj
            if isinstance(obj, DPMF):
                self.dpmf[name] = obj
            if isinstance(obj, MC):
                self.mc[name] = obj
            if isinstance(obj, MX):
                self.mx[name] = obj
            if isinstance(obj, NameCollection):
                self.name_collection[name] = obj

    def generate_mean(self):
        if len(self.mean) == 0:
            return []

        means = ["MEAN_IN_FILE inline"]
        means.append(str(len(self.mean)) + "\n")
        for key_index in range(len(list(self.mean))):
            means.append(
                self.mean[list(self.mean)[key_index]].generate(key_index))
        return "\n".join(means)

    def generate_covar(self):
        if len(self.covar) == 0:
            return []

        covars = ["COVAR_IN_FILE inline"]
        covars.append(str(len(self.covar)) + "\n")

        for key_index in range(len(list(self.covar))):
            covars.append(
                self.covar[list(self.covar)[key_index]].generate(key_index))
        return "\n".join(covars)

    def generate_dense(self):
        if len(self.dense) == 0:
            return []

        dense_cpts = ["DENSE_CPT_IN_FILE inline"]
        dense_cpts.append(str(len(self.dense)) + "\n")

        for key_index in range(len(list(self.dense))):
            dense_cpts.append(
                self.dense[list(self.dense)[key_index]].generate(key_index))
        return "\n".join(dense_cpts)

    def generate_deterministic(self):
        if len(self.deterministic) == 0:
            return []

        det_cpts = ["DETERMINISTIC_CPT_IN_FILE inline"]
        det_cpts.append(str(len(self.deterministic)) + "\n")

        for key_index in range(len(list(self.deterministic))):
            det_cpts.append(self.deterministic[
                                list(self.deterministic)[key_index]].generate(
                key_index))
        return "\n".join(det_cpts)

    def generate_dpmf(self):
        if len(self.dpmf) == 0:
            return []

        dpmfs = ["DPMF_IN_FILE inline"]
        dpmfs.append(str(len(self.dpmf)) + "\n")

        for key_index in range(len(list(self.dpmf))):
            dpmfs.append(
                self.dpmf[list(self.dpmf)[key_index]].generate(key_index))
        return "\n".join(dpmfs)

    def generate_mc(self):
        if len(self.mc) == 0:
            return []

        mcs = ["MC_IN_FILE inline"]
        mcs.append(str(len(self.mc)) + "\n")

        for key_index in range(len(list(self.mc))):
            mcs.append(self.mc[list(self.mc)[key_index]].generate(key_index))

        return "\n".join(mcs)

    def generate_mx(self):
        if len(self.mx) == 0:
            return []

        mxs = ["MX_IN_FILE inline"]
        mxs.append(str(len(self.mx)) + "\n")

        for key_index in range(len(list(self.mx))):
            mxs.append(self.mx[list(self.mx)[key_index]].generate(key_index))
        return "\n".join(mxs)

    def generate_name_col(self):
        if len(self.name_collection) == 0:
            return []

        collections = ["NAME_COLLECTION_IN_FILE inline"]
        collections.append(str(len(self.name_collection)) + "\n")

        for key_index in range(len(list(self.name_collection))):
            collections.append(self.name_collection[list(self.name_collection)[
                key_index]].generate(key_index))

        return "\n".join(collections)

    def __str__(self):
        attrs_gen = [self.generate_name_col(), self.generate_deterministic(),
                     self.generate_dense(), self.generate_mean(),
                     self.generate_covar(), self.generate_dpmf(),
                     self.generate_mc(), self.generate_mx()]
        s = []
        for obj in attrs_gen:
            s.append("".join(obj))

        return "".join(s)

