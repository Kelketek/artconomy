import { formRegistry } from "./registry.ts"
import { FieldController } from "./field-controller.ts"
import deepEqual from "fast-deep-equal"
import { artCall } from "@/lib/lib.ts"

import { RawData } from "@/store/forms/types/main"

export function required(field: FieldController): string[] {
  if (!field.value) {
    return ["This field may not be blank."]
  }
  return []
}

export function email(field: FieldController): string[] {
  if (field.value.trim() === "") {
    // Should be handled by the required validator instead.
    return []
  }
  const parts = field.value.split("@")
  if (parts.length !== 2) {
    return ["Emails must contain an @ in the middle."]
  }
  const front = parts[0].trimLeft()
  const back = parts[1].trimRight()
  if (front.length === 0) {
    return ["You must include the username in front of the @."]
  }
  if (back.length === 0) {
    return ["You must include the domain name after the @."]
  }
  if (front.search(/\s/g) !== -1) {
    return ["Emails cannot have a space in the section before the @."]
  }
  if (back.search(/\s/g) !== -1) {
    return ["Emails cannot have a space in the section after the @."]
  }
  if (back.indexOf(".") === -1) {
    return [
      "Emails without a full domain are not supported. (Did you forget the .com?)",
    ]
  }
  return []
}

export type CardType =
  | "mastercard"
  | "amex"
  | "discover"
  | "visa"
  | "diners"
  | "unknown"

export function matches(
  field: FieldController,
  fieldName: string,
  error: string,
) {
  if (!deepEqual(field.value, field.form.fields[fieldName].value)) {
    return [error || "Values do not match."]
  }
  return []
}

export function validateStatus(status: number) {
  if (status >= 200 && status < 300) {
    return true
  }
  return status === 400
}

export function simpleAsyncValidator(url: string) {
  return async (
    field: FieldController,
    signal: AbortSignal,
    sendAs?: string,
  ): Promise<string[]> => {
    const data: RawData = {}
    sendAs = sendAs || field.fieldName
    data[sendAs] = field.value
    return artCall({ url, method: "post", data, signal, validateStatus }).then(
      (responseData: any) => {
        return responseData[sendAs as string] || []
      },
    )
  }
}

export function numeric(field: FieldController) {
  let value = field.value + ""
  value = value.trim()
  if (/^[-]?[0-9]*[.]?[0-9]*$/.test(value)) {
    return []
  }
  return ["Numbers only, please."]
}

export function minLength(field: FieldController, min: number) {
  const value = field.value.trim()
  if (value.length < min) {
    return [`Too short. Minimum length: ${min}.`]
  }
  return []
}

export function maxLength(field: FieldController, max: number) {
  const value = field.value.trim()
  if (value.length > max) {
    return [`Too long. Maximum length: ${max}.`]
  }
  return []
}

export function colorRef(field: FieldController) {
  const ref = field.value.trim()
  if (/^[#][0-9a-fA-F]{6}$/.test(ref)) {
    return []
  }
  return [
    "The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.",
  ]
}

export const emailAsync = simpleAsyncValidator(
  "/api/profiles/form-validators/email/",
)
export const username = simpleAsyncValidator(
  "/api/profiles/form-validators/username/",
)
export const password = simpleAsyncValidator(
  "/api/profiles/form-validators/password/",
)

export function registerValidators() {
  formRegistry.validators.required = required
  formRegistry.validators.email = email
  formRegistry.validators.matches = matches
  formRegistry.validators.colorRef = colorRef
  formRegistry.validators.numeric = numeric
  formRegistry.validators.minLength = minLength
  formRegistry.validators.maxLength = maxLength
  formRegistry.asyncValidators.username = username
  formRegistry.asyncValidators.email = emailAsync
  formRegistry.asyncValidators.password = password
}
