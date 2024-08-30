import {ArtState as RootState} from '../artState.ts'
import {ActionTree, GetterTree, MutationTree} from 'vuex'
import cloneDeep from 'lodash/cloneDeep'
import isEqual from 'lodash/isEqual'
import {artCall} from '@/lib/lib.ts'
import {FormSchema} from './types/FormSchema.ts'
import {MetaToggles} from '@/store/forms/types/MetaToggles.ts'
import {FieldSet} from '@/store/forms/types/FieldSet.ts'
import {FormError} from '@/store/forms/types/FormError.ts'
import {FormErrorSet} from '@/store/forms/types/FormErrorSet.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {FieldSchema} from '@/store/forms/types/FieldSchema.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import {RootFormState} from '@/store/forms/types/RootFormState.ts'
import {Field} from '@/store/forms/types/Field.ts'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs.ts'

const getters: GetterTree<RootFormState, RootState> = {}

export function fieldFromSchema(schema: FieldSchema): Field {
  return {
    ...{
      disabled: false,
      validators: [],
      errors: [],
      hidden: false,
      initialData: cloneDeep(schema.value),
      extra: {},
      debounce: null,
      step: 1,
    },
    ...schema,
  }
}

function setFieldErrors(state: RootFormState, name: string, fieldErrors: FormError) {
  let step = state[name].step
  for (const key of Object.keys(state[name].fields)) {
    state[name].fields[key].errors = (fieldErrors && fieldErrors[key]) || []
    if (!state[name].fields[key].errors.length) {
      continue
    }
    const fieldStep = state[name].fields[key].step
    if (fieldStep < step) {
      step = fieldStep
    }
  }
  state[name].step = step
}

// noinspection JSUnusedGlobalSymbols
const mutations: MutationTree<RootFormState> = {
  initForm(state: RootFormState, payload: FormSchema) {
    // Creates new state tracking information for a form.
    const fields: FieldSet = {}
    for (const field of Object.keys(payload.fields)) {
      fields[field] = fieldFromSchema(payload.fields[field])
    }
    const defaults = {
      reset: true,
      debounce: 500,
      persistent: false,
      submitted: false,
      disabled: false,
      method: 'post' as HttpVerbs,
      errors: [],
      sending: false,
      step: 1,
    }
    state[payload.name] = {...defaults, ...payload, ...{fields}}
  },
  delForm(state: RootFormState, payload: { name: string }) {
    delete state[payload.name]
  },
  setErrors(state: RootFormState, payload: { name: string, errors: FormErrorSet }) {
    // Sets the errors across an entire form. Fills in blanks for any missing fields.
    /* istanbul ignore if */
    if (state[payload.name] === undefined) {
      // Form was unloaded, no place to set errors.
      return
    }
    const errorSet: FormErrorSet = {errors: [], fields: {}}
    setFieldErrors(state, payload.name, payload.errors.fields)
    errorSet.errors = payload.errors.errors || []
    state[payload.name].errors = errorSet.errors
  },
  setEndpoint(state: RootFormState, payload: { name: string, endpoint: string }) {
    state[payload.name].endpoint = payload.endpoint
  },
  setStep(state: RootFormState, payload: { name: string, step: number }) {
    state[payload.name].step = payload.step
  },
  clearErrors(state: RootFormState, payload: { name: string }) {
    state[payload.name].errors = []
    for (const key of Object.keys(state[payload.name].fields)) {
      state[payload.name].fields[key].errors = []
    }
  },
  setFieldErrors(state: RootFormState, payload: { name: string, fields: FormError }) {
    /* istanbul ignore if */
    if (state[payload.name] === undefined) {
      // Form was unloaded. No place to set errors.
      return
    }
    // Sets the errors on a particular field.
    setFieldErrors(state, payload.name, payload.fields)
  },
  updateMeta(state: RootFormState, payload: { name: string, meta: { [key in keyof typeof MetaToggles]: boolean } }) {
    for (const key of Object.keys(payload.meta)) {
      // @ts-ignore
      state[payload.name][key] = payload.meta[key]
    }
  },
  setMetaErrors(state: RootFormState, payload: { name: string, errors: [] }) {
    // Sets the meta form errors, such as those for connection issues.
    state[payload.name].errors = cloneDeep(payload.errors)
  },
  updateValues(state: RootFormState, payload: { name: string, data: RawData }) {
    // Updates the data to contain whatever additional information is given.
    for (const key of Object.keys(payload.data)) {
      state[payload.name].fields[key].value = payload.data[key]
    }
  },
  updateInitialData(state: RootFormState, payload: { name: string, data: RawData }) {
    // Updates the data to contain whatever additional information is given.
    for (const key of Object.keys(payload.data)) {
      state[payload.name].fields[key].initialData = payload.data[key]
    }
  },
  addField(state: RootFormState, payload: {
             name: string, field: { name: string, schema: FieldSchema },
           },
  ) {
    // Adds a field to the form, with whatever data and optionally with errors pre-added.
    state[payload.name].fields[payload.field.name] = fieldFromSchema(payload.field.schema)
  },
  delField(state: RootFormState, payload: { name: string, field: string }) {
    // Deletes a field from a form.
    delete state[payload.name].fields[payload.field]
  },
  resetForm(state: RootFormState, payload: { name: string }) {
    for (const field of Object.values(state[payload.name].fields)) {
      field.value = field.initialData
    }
    state[payload.name].step = 1
  },
}

export function dataFromForm(form: FormState) {
  const data: { [key: string]: any } = {}
  for (const key of Object.keys(form.fields)) {
    if (form.fields[key].omitIf !== undefined) {
      if (isEqual(form.fields[key].value, form.fields[key].omitIf)) {
        continue
      }
    }
    data[key] = form.fields[key].value
  }
  return data
}

const actions: ActionTree<RootFormState, RootState> = {
  async submit({state, commit}, payload: { name: string }) {
    // Submits the form, and sets
    const form = state[payload.name]
    const data = dataFromForm(form)
    commit('updateMeta', {name: payload.name, meta: {sending: true}})
    return artCall({url: form.endpoint, method: form.method, data}).then((response) => {
      if (form.reset) {
        commit('resetForm', {name: payload.name})
      }
      commit('clearErrors', {name: payload.name})
      commit('updateMeta', {name: payload.name, meta: {sending: false}})
      return response
    })
  },
}

export const forms = {
  namespaced: true,
  state: () => ({}),
  getters,
  actions,
  mutations,
}
