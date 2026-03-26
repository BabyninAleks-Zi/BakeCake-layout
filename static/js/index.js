const builderData = window.BUILDER_DATA || {}

const builderApp = Vue.createApp({
    name: "App",
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            schema1: {
                lvls: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' количество уровней';
                },
                form: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' форму торта';
                },
                topping: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' топпинг';
                }
            },
            schema2: {
                name: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' имя';
                },
                phone: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' телефон';
                },
                name_format: (value) => {
                    const regex = /^[a-zA-Zа-яА-Я]+$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат имени нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат почты нарушен';
                    }
                    return true;
                },
                phone_format:(value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                },
                email: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' почту';
                },
                address: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' адрес';
                },
                date: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' дату доставки';
                },
                time: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' время доставки';
                },
                personal_data_consent: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' согласие на обработку данных';
                }
            },
            DATA: builderData.labels || {
                Levels: {},
                Forms: {},
                Toppings: {},
                Berries: {},
                Decors: {}
            },
            Costs: builderData.costs || {
                Levels: {},
                Forms: {},
                Toppings: {},
                Berries: {},
                Decors: {},
                Words: 500
            },
            Levels: '',
            Form: '',
            Topping: '',
            Berries: '',
            Decor: '',
            Words: '',
            Comments: '',
            Designed: false,

            Name: '',
            Phone: null,
            Email: null,
            Address: null,
            Dates: null,
            Time: null,
            DelivComments: '',
            PersonalDataConsent: false
        }
    },
    methods: {
        ToStep4() {
            this.Designed = true
            setTimeout(() => this.$refs.ToStep4.click(), 0);
        },
        getOptionPrice(groupName, optionId) {
            const group = this.Costs[groupName] || {}
            const key = String(optionId || '')
            const price = group[key]

            if (price === undefined || price === null || price === '') {
                return 0
            }

            const normalizedPrice = Number(price)
            return Number.isNaN(normalizedPrice) ? 0 : normalizedPrice
        }
    },
    computed: {
        Cost() {
            let inscriptionPrice = this.Words ? this.Costs.Words : 0

            return this.getOptionPrice('Levels', this.Levels) +
                this.getOptionPrice('Forms', this.Form) +
                this.getOptionPrice('Toppings', this.Topping) +
                this.getOptionPrice('Berries', this.Berries) +
                this.getOptionPrice('Decors', this.Decor) +
                Number(inscriptionPrice)
        }
    }
})

builderApp.config.compilerOptions.delimiters = ['[[', ']]']
builderApp.mount('#VueApp')
