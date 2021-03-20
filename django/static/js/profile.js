function get_age(date) {
    let diff = Date.now() - date.getTime();
    let ageDate = new Date(diff);
    let actualAge = Math.abs(ageDate.getUTCFullYear() - 1970);
    return actualAge;
}